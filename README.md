**Run with bash**
for C in $(cat country_labels.txt); do
    LINES=$(wc -l < CHUNKSDIR/{C}_chunks.txt)
    sbatch --array=0-$((LINES-1)) submit_health_linear_v01.sh $C
done


