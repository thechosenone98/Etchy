#!/bin/zsh
. /Users/zach-mcc/Documents/Programming/Python/Etchy/EtchyEnv/bin/activate
echo "Where to save files: "
read OUTPUT_LOCATION
mkdir $OUTPUT_LOCATION
cd $OUTPUT_LOCATION
mkdir "OUTPUT_EPS"
mkdir "OUTPUT_PDF"

counter=0
for i in $(seq 1.0 0.0001 1.05); do
    echo $i
    padded_num=$(printf "%05d" $counter)
    python /Users/zach-mcc/Documents/Programming/Python/Etchy/number_decimal_drawing.py --inputfile ../790831.txt --outputfile 790831_${padded_num}.tcode --multfactor $i
    sleep 0.5s
    cd "OUTPUT_EPS"
    python /Users/zach-mcc/Documents/Programming/Python/Etchy/etchy.py --inputfile ../790831_${padded_num}.tcode --outputfile 790831_${padded_num}.eps --parser TCODE
    sleep 0.5s
    gs -sDEVICE=pdfwrite -dEPSCrop -o 790831_${padded_num}.pdf 790831_${padded_num}.eps
    cpdf -scale-page "0.05 0.05" 790831_${padded_num}.pdf -o 790831_${padded_num}_rescaled.pdf
    pdfcrop --bbox "$(<bbox_tmp.txt)" 790831_${padded_num}_rescaled.pdf
    rm 790831_${padded_num}.pdf
    rm 790831_${padded_num}_rescaled.pdf
    cd ..
    counter=$(($counter+1))
    echo $padded_num
    sleep 1s
done

cd "OUTPUT_EPS"
gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=output.pdf *.pdf
mv "output.pdf" "../OUTPUT_PDF/output.pdf"
cd "../OUTPUT_PDF/"
mkdir "OUTPUT_PNGs"
gs -dNOPAUSE -dBATCH -sDEVICE=png16m -sOutputFile="OUTPUT_PNGs/790831-%05d.png" output.pdf
cd "OUTPUT_PNGs"
# Find biggest width and height out of all the images in the folder
W_MAX=0
H_MAX=0
for FILE in *;
do
    if [[ $FILE == *.png ]]
    then
        dim=$(identify -format '%w %h' $FILE)
        read -r W H <<< $dim
        if [[ $W > $W_MAX ]]
        then
            W_MAX=$W
        fi
        if [[ $H > $H_MAX ]]
        then
            H_MAX=$H
        fi
        echo "$W""x""$H"
    fi
done

# Pad the dimensions with white borders to fit the W_MAX x H_MAX found previously
for FILE in *;
do
    if [[ $FILE == *.png ]]
    then
        dim=$(identify -format '%w %h' $FILE)
        read -r W H <<< $dim
        BORDER_SIZE_HORIZONTAL=$((($W_MAX-$W)/2))
        BORDER_SIZE_VERTICAL=$((($H_MAX-$H)/2))
        # Create new name for output file
        filename=$(basename -- "$FILE")
        output_filename="${filename%.*}"
        output_filename+="-resized.png"
        echo "CREATING: $output_filename"
        convert -bordercolor white -border $BORDER_SIZE_HORIZONTAL"x"$BORDER_SIZE_VERTICAL $FILE $output_filename
        rm $FILE
    fi
done
# Create gif with all the padded images in the folder
convert -delay 5 -loop 0 *.png animation.gif