#!/bin/bash

# All of the IMDB predicates are currently stored as facts, we need to separate positive/negative to train/test.

for i in {1..5}; do
    cd test${i}
    
    mv test${i}_imdb_bk.txt test${i}_bk.txt
    mv test${i}_imdb_pos.txt test${i}_pos.txt
    mv test${i}_imdb_neg.txt test${i}_neg.txt
    mv test${i}_imdb_facts.txt test${i}_facts.txt
    
    cd ..
done

if false; then
for i in {1..5}; do
    cd train${i}
    
    mv train${i}_imdb_bk.txt train${i}_bk.txt
    mv train${i}_imdb_pos.txt train${i}_pos.txt
    mv train${i}_imdb_neg.txt train${i}_neg.txt
    mv train${i}_imdb_facts.txt train${i}_facts.txt
    
    cd ..
done
fi

function splitWorkedUnder() {
    
    # Roughly: workedunder([actor], [director]).
    #          genre([director], [genre]).
    # Closed World Assumption: if a person did not explicitly work under another person, they did not.

    for i in {1..5}; do

	for j in train test; do
	    
	    DIR="${j}${i}"
	    
	    # Step 1: Remove any commented-out predicates from the facts, and sort to remove duplicates.
	    grep -v '^//' "${DIR}/${j}${i}_facts.txt" | sort -u > temp && mv temp "${DIR}/${j}${i}_facts.txt"
	    
	    # Step 2: Pull the "workedunder" and "genre" predicates

	done
    done
}

function splitActorGender() {
    
    # Closed World Assumption: if an actor is not female, he is male.
    
    # Add female_gender from facts to *pos.txt
    # Label non-female actors as female, and add the newly created predicates to *neg.txt
    
    for i in {1..5}; do
	
	for j in train test; do
	
	    DIR="${j}${i}"
	    
	    # Remove any commented-out predicates from the facts.
	    grep -v '^//' "${DIR}/${j}${i}_facts.txt" > temp && mv temp "${DIR}/${j}${i}_facts.txt"
	    
	    # Sort and remove any dupliate facts.
	    sort -u "${DIR}/${j}${i}_facts.txt" > temp && mv temp "${DIR}/${j}${i}_facts.txt"
	    
	    # Pull the female_gender predicates out of the facts.
	    grep "^female_gender" "${DIR}/${j}${i}_facts.txt" | cut -d '(' -f 2 | cut -d ')' -f 1 > ALL_female.txt
	    
	    # Pull the actor predicates out of the facts so we can label negative examples with the males.
	    grep "^actor" "${DIR}/${j}${i}_facts.txt" | cut -d '(' -f 2 | cut -d ')' -f 1 > ALL_actors.txt
	    
	    # Male actors are those which are present in ALL_actors but not present in ALL_female
	    diff --new-line-format="" --unchanged-line-format="" ALL_actors.txt ALL_female.txt > ALL_male.txt
	    
	    # Do some cleanup and fix all of the files.
	    mv ALL_male.txt "${DIR}/${j}${i}_neg.txt"
	    mv ALL_female.txt "${DIR}/${j}${i}_pos.txt"
	    rm -f ALL_actors.txt
	    
	    # Remove the female_gender predicates from the facts.
	    grep -v "^female_gender" "${DIR}/${j}${i}_facts.txt" > temp && mv temp "${DIR}/${j}${i}_facts.txt"
	    
	    # Wrap the lines in: female_gender( ... ).
	    sed -i 's/^/female_gender(/' "${DIR}/${j}${i}_pos.txt"
	    sed -i 's/^/female_gender(/' "${DIR}/${j}${i}_neg.txt"
	    
	    sed -i 's/$/)./' "${DIR}/${j}${i}_pos.txt"
	    sed -i 's/$/)./' "${DIR}/${j}${i}_neg.txt"
	done
    done
}
