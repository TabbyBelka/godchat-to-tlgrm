>pipe
>log
QUERY_STRING='token=testtoken&text=[[0,"Belka","Hi!"], [120,"Belka",":00!"], [60,"Belka","Hi!"]]' FRONTEND_CONFIG=frontendconfig.test.cfg python3 mes.py
if grep -q '^\[0, "Belka", "Hi!"\]' pipe; then
  echo 'success!';
#  rm pipe log
else
  echo 'fail!';
  exit 1
fi
