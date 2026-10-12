import os,pty,fcntl,termios,struct,subprocess,select,time,json,resource,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def probe(mode,width,height,fps=60,seconds=2,trace=False,keys=b"",binary=None, bytes_per_second=None):
    if binary is None: raise ValueError("An instrumented binary is required")
    master,slave=pty.openpty()
    fcntl.ioctl(slave,termios.TIOCSWINSZ,struct.pack("HHHH",height,width,0,0))
    argv=[binary,"--no-name","--seed","42","--fps",str(fps),"--mode",mode]
    logfile=ROOT/f"trace-{mode}-{width}x{height}.txt"
    if trace: argv=["strace","-qq","-f","-c","-o",str(logfile),*argv]
    env=os.environ.copy();env["TERM"]="xterm-256color"
    p=subprocess.Popen(argv,stdin=slave,stdout=slave,stderr=slave,env=env,close_fds=True)
    os.close(slave)
    start=time.monotonic(); frames=[]; total=0; tail=b""; raw=bytearray(); sent=False
    while time.monotonic()-start < seconds:
        if select.select([master],[],[],.05)[0]:
            try: data=os.read(master,262144)
            except OSError: break
            now=time.monotonic();total+=len(data);raw.extend(data)
            if bytes_per_second: time.sleep(len(data)/bytes_per_second)
            joined=tail+data
            count=joined.count(b"\x1b]777;rmatrix-frame\x07")
            frames.extend([now]*count)
            tail=joined[-(len(b"\x1b]777;rmatrix-frame\x07")-1):]
        if keys and not sent and len(frames)>3:
            os.write(master,keys);sent=True
    stop=time.monotonic()
    stat=Path(f"/proc/{p.pid}/stat").read_text().rsplit(")",1)[1].split()
    observed_cpu=(int(stat[11])+int(stat[12]))/os.sysconf("SC_CLK_TCK")
    rss_kib=int(stat[21])*os.sysconf("SC_PAGE_SIZE")/1024
    os.write(master,b"q")
    deadline=stop+10
    while p.poll() is None and time.monotonic()<deadline:
        if select.select([master],[],[],.1)[0]:
            try: os.read(master,262144)
            except OSError: break
    if p.poll() is None:
        p.kill()
    pid,status,usage=os.wait4(p.pid,0) if p.returncode is None else (p.pid,0,None)
    if usage is None:
        # poll() may have reaped it; collect CPU from /proc before quit in later runs.
        cpu=None
    else: cpu=usage.ru_utime+usage.ru_stime
    os.close(master)
    intervals=[b-a for a,b in zip(frames,frames[1:]) if b>a]
    result={"mode":mode,"size":[width,height],"target_fps":fps,"frames":len(frames),
            "observed_fps":round((len(frames)-1)/(frames[-1]-frames[0]),2) if len(frames)>1 else 0,
            "median_frame_ms":round(statistics.median(intervals)*1000,2) if intervals else 0,
            "p95_frame_ms":round(sorted(intervals)[int(.95*(len(intervals)-1))]*1000,2) if intervals else 0,
            "output_bytes":total,"output_MiB_per_second":round(total/(stop-start)/1048576,3),
            "cpu_seconds":observed_cpu,"rss_kib":rss_kib,"read_limit_bytes_per_second":bytes_per_second,"wall_seconds":stop-start,"keys":keys.decode()}
    assert b"Ramos runtime error" not in raw,raw[-1000:]
    print(json.dumps(result),flush=True)
    return result
