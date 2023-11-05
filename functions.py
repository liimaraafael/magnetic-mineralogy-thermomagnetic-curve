import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def derivative(row):
    if row["TEMP"] == row["TEMP_novo"]:
        return np.nan

    else:
        return (row["K_Kmax_novo"] - row["K_Kmax"]) / (row["TEMP_novo"] - row["TEMP"])


def calculate(dataframe, file_name):
    dataframe["K_Kmax"] = dataframe["CSUSC"] / dataframe["CSUSC"].max()
    dataframe["K_Kmax_novo"] = dataframe["K_Kmax"].shift(1)
    dataframe["TEMP_novo"] = dataframe["TEMP"].shift(1)
    dataframe["dK_dt"] = dataframe.apply(derivative, axis=1)
    dataframe = dataframe.drop(columns=["K_Kmax_novo", "TEMP_novo"])

    dataframe.to_excel("output-data/xlsx/" + str(file_name) + ".xlsx", index=False)

    return dataframe


def trait_file(file_clw, file_cur, file_name):
    row_file_clw = open("input-data/" + str(file_clw), "r")
    row_file_cur = open("input-data/" + str(file_cur), "r")

    rowdata_clw = row_file_clw.readlines(0)
    rowdata_cur = row_file_cur.readlines(0)
    treated = []
    treated1 = []

    for rowdata in [rowdata_clw, rowdata_cur]:
        i = 0

        for line in rowdata:
            if i > 0:

                for trait in line.replace("\n", "").replace(" ", ",").split(","):

                    if len(trait) > 1:
                        treated1.append(trait)

                treated.append(treated1)
                treated1 = []
            i += 1

    treated_df = pd.DataFrame(
        treated,
        columns=["TEMP", "TSUSC", "CSUSC", "NSUSC", "BULKS", "FERRT", "FERRB", "TIME", "EMPTY"]
    )

    treated_df["TEMP"] = treated_df["TEMP"].astype(float)
    treated_df["CSUSC"] = treated_df["CSUSC"].astype(float)
    treated_df = treated_df.drop(columns=["TSUSC", "NSUSC", "BULKS", "FERRT", "FERRB", "TIME", "EMPTY"])

    return calculate(treated_df, file_name)


def plot(df, name):
    index_dict = dict(zip(df["TEMP"], df.index))
    temp_dict = dict(zip(df["dK_dt"], df["TEMP"]))

    index_temp_max = index_dict.get(df.TEMP.max())
    df_heating = df.iloc[:index_temp_max]
    df_cooling = df.iloc[index_temp_max + 1:]

    x_curie = df["TEMP"].max() * 0.50
    y_curie = df["dK_dt"].min()

    x_verveine = df["TEMP"].min() * 0.50
    y_verveine = df["dK_dt"].min()

    fig, ax1 = plt.subplots()

    ax1.plot(df_heating["TEMP"], df_heating["CSUSC"], label='Heating', color='red', linewidth=0.8)
    ax1.plot(df_cooling["TEMP"], df_cooling["CSUSC"], label='Cooling', color='blue', linewidth=0.8)
    ax1.legend(loc='upper right')
    ax1.set_ylabel(r'Normalized susceptibility $\left(\frac{m^{3}}{kg}\right)$', fontsize=12)
    ax1.set_xlabel(r'Temperature $\left(^{o}C\right)$', fontsize=12)
    ax1.yaxis.major.formatter._useMathText = True
    ax1.ticklabel_format(style='sci', scilimits=(-3, 4), axis='both')

    ax2 = ax1.twinx()
    ax2.plot(df["TEMP"], df["dK_dt"], color='gray', linewidth=0.8, alpha=0.6)
    ax2.set_ylabel(r'$dK/dt$', fontsize=12)
    ax2.vlines(temp_dict.get(df["dK_dt"].min()), df["dK_dt"].min() + df["dK_dt"].min() * 0.15,
               df["dK_dt"].max() + df["dK_dt"].max() * 0.15, alpha=0.8, linestyle='dashed', linewidth=1, color='black')
    ax2.vlines(temp_dict.get(df["dK_dt"].max()), df["dK_dt"].min() + df["dK_dt"].min() * 0.15,
               df["dK_dt"].max() + df["dK_dt"].max() * 0.15, alpha=0.8, linestyle='dashed', linewidth=1, color='black')
    ax2.yaxis.major.formatter._useMathText = True
    ax2.ticklabel_format(style='sci', scilimits=(-3, 4), axis='both')

    ax2.text(x_curie, y_curie, r'$T_{c} =' + str(temp_dict.get(df["dK_dt"].min())) + '^{o}C$',
             backgroundcolor='white')
    ax2.text(x_verveine, y_verveine, r'$T_{v} =' + str(temp_dict.get(df["dK_dt"].max())) + '^{o}C$',
             backgroundcolor='white')

    plt.tight_layout()
    plt.gcf().set_size_inches(8, 5)
    plt.savefig("output-data/image/png/" + name + ".png", format='png', dpi=500)
    plt.savefig("output-data/image/pdf/" + name + ".pdf", format='pdf', dpi=500)
    plt.savefig("output-data/image/svg/" + name + ".svg", format='svg', dpi=500)
    plt.close()
