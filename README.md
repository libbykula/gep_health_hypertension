# Global GEP Physical Health 

Estimating the value of urban nature in terms of avoided hypertension costs. 

# Run 

```bash
for C in $(cat country_labels.txt); do
    LINES=$(wc -l < CHUNKSDIR/{C}_chunks.txt)
    sbatch --array=0-$((LINES-1)) submit_health_linear_v01.sh $C
done
---

