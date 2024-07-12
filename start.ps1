conda env create --prefix .conda --file freeze.yml

conda activate .\.conda

python main.py
