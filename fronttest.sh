>pipe
>log
FTIME=$(date -u -d '+3 hours' +%s)
STIME=$(($FTIME+60))
TTIME=$(($FTIME+30))
DTIMER=$((($STIME+120)/60%60))
CDTIMER=$((($STIME+180)/60%60))
FOTIME=$(($FTIME+90))
if ((DTIMER < 10)); then
  DTIMER=0$DTIMER 	
fi
if ((CDTIMER < 10)); then
  CDTIMER=0$DTIMER 	
fi
QUERY_STRING="token=testtoken&text=[[$FTIME,\"Belka\",\"Hi!\", 0], [$STIME,\"Belka\",\":$CDTIMER!\"],[$STIME,\"Belka\",\":$DTIMER!\"], [$TTIME,\"Belka\",\"Hi!\"], [$FOTIME,\"B\", \"отменА:$CDTIMER\"]]" FRONTEND_CONFIG=frontendconfig.test.cfg python3 mes.py
if grep -q "^\[$FTIME, \"Belka\", \"Hi!\", 0\]" pipe; then
  echo 'success!';
#  rm pipe log
else
  echo 'fail!';
  exit 1
fi
