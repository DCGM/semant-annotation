
P=stats

for D in 2023-11-01_2023-11-20 2023-11-20_2023-11-27 2023-11-27_2023-12-04 2023-12-04_2023-12-11
do 
	START=$(echo $D | cut -f 1 -d _)
	END=$(echo $D | cut -f 2 -d _) 
	anotator=./${P}/anotator/$D
	python stats.py -l michal.hradis -p random5digital -s $START -e $END -k 300 -u https://anotator.semant.cz/api/ -o $anotator
	text_search=$(find ${P}/text_search/ | grep $D)
	image_search=$(find ${P}/image_search/ | grep $D)
	faces=$(find ${P}/faces/ | grep $D)
	python mergejson.py --input-json-files $text_search $image_search $faces --input-stats-file $anotator.jsonl -o merged_$D.jsonl --from-date $START --to-date $END
done 
