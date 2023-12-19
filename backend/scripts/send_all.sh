for week in *.jsonl
do 
  from=$(echo $week | cut -f 2 -d _)
  to=$(echo $week | cut -f 3 -d _ | cut -f 1 -d \.)
  python send_email.py -l ihradis -p ${PASS} --mail-server kazi.fit.vutbr.cz \
  	--subject "[semANT] Statistiky Vaseho anotovani pro AI $from - $to" \
  	--template mail_template.txt < $week >log_${from}_${to}.txt 2>&1
done
