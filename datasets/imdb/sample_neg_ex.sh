#!/bin/bash

echo "you may need to change how things are commented."

if false; then
    
    for i in {1..5}; do
	
	DIR="test${i}"
	
	# Remove any commented-out predicates from the facts.
	grep -v '^//' "${DIR}/test${i}_facts.txt" > temp && mv temp "${DIR}/test${i}_facts.txt"
	
	# Sort and remove any dupliate facts.
	sort -u "${DIR}/test${i}_facts.txt" > temp && mv temp "${DIR}/test${i}_facts.txt"
	
	# Pull the female_gender predicates out of the facts.
	grep "^female_gender" "${DIR}/test${i}_facts.txt" | cut -d '(' -f 2 | cut -d ')' -f 1 > ALL_female.txt
	
	# Pull the actor predicates out of the facts so we can label negative examples with the males.
	grep "^actor" "${DIR}/test${i}_facts.txt" | cut -d '(' -f 2 | cut -d ')' -f 1 > ALL_actors.txt
	
	# Male actors are those which are present in ALL_actors but not present in ALL_female
	diff --new-line-format="" --unchanged-line-format="" ALL_actors.txt ALL_female.txt > ALL_male.txt
	
	# Do some cleanup and fix all of the files.
	mv ALL_male.txt "${DIR}/test${i}_neg.txt"
	mv ALL_female.txt "${DIR}/test${i}_pos.txt"
	rm -f ALL_actors.txt
	
	# Remove the female_gender predicates from the facts.
	grep -v "^female_gender" "${DIR}/test${i}_facts.txt" > temp && mv temp "${DIR}/test${i}_facts.txt"
	
    done
fi

if false; then

    for i in {1..5}; do
	
	DIR="test${i}"
	
	sed -i 's/^/female_gender(/' "${DIR}/test${i}_pos.txt"
	sed -i 's/^/female_gender(/' "${DIR}/test${i}_neg.txt"
	
	sed -i 's/$/)./' "${DIR}/test${i}_pos.txt"
	sed -i 's/$/)./' "${DIR}/test${i}_neg.txt"
	
    done
fi
