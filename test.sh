echo _____START_____
for file in ./react_examples/*; do
	echo $file:
	echo Start Us
	venv/bin/python react_mc.py $file
	if test $? -ne 0
	then
		exit 1
	fi
	echo End Us
	echo
done
echo _____END_____
exit 0
