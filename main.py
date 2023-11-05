from constants import list_clw, list_cur, list_name
from functions import trait_file, plot

for name, clw, cur in zip(list_name, list_clw, list_cur):
    df = trait_file(clw, cur, name)
    plot(df, name)
