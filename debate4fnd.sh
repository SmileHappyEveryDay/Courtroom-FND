set -e
set -u

FND_PATH=/Your-Workspace/Courtroom-FND

python3 $FND_PATH/code/courtroomdebate4fnd.py \
    -i $FND_PATH/data/FakeNewsDataset/input.example.txt \
    -o $FND_PATH/data/FakeNewsDataset/output \
    -k Your-OpenAI-Api-Key \