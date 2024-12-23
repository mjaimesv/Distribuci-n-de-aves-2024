"""
Pregunta biológica:
¿Como varía la riqueza de aves en Colombia en el año 2024 y que familia es más
predominante en cada región(departamento) del país?¿Hay diferencias significativas en cuanto a familias
entre las regiones?

Gráficas importantes para responder la pregunta biológica:
1. Top 10 familias mas numerosas en Colombia: contar individuos por ocurrencia.
2. Proporción de familias por región (provinceState): Aquí definimos que familia es más predominante.
3. Diferencias significativas entre regiones de la familia más predominante.
4. Familias por departamento de Colombia en cada mes del año 2024.
5. Distribución de las familias más numerosas de Colombia de acuerdo a la altitud(m.s.n.m).
6. Como extra quise crear una serie de valores aleatorios de conteo de individuos por familias(top 10 familias), para
compararlos con los valores reales y ver como difiere.

"""
#Importar las librerías necesarias al inicio:
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import kruskal, f_oneway

# Cargar el archivo CSV para su lectura:
datos = "aves_colombia.csv"
df = pd.read_csv(datos, sep='\t', low_memory=False)

# Definir variables
family_counts = df.groupby('family')['individualCount'].sum().sort_values(ascending=False)
top_10_familias = family_counts.nlargest(10).index
family_stateProvince = df.groupby(['family', 'stateProvince']).size().reset_index(name='counts')

# Crear el archivo PDF
pdf_file = "analisis_aves_colombia.pdf"
with PdfPages(pdf_file) as pdf:
    # Página inicial con texto introductorio
    plt.figure(figsize=(8.5, 11))
    plt.axis('off')  # Ocultar ejes

    # Título en la parte superior de la página
    plt.text(0.5, 1, "Análisis de Aves en Colombia - 2024", fontsize=18, weight='bold', ha='center', va='center')

    # Texto introductorio más abajo
    plt.text(0.5, 0.3, (
        "Este documento contiene un análisis gráfico detallado de los datos de observación de aves en Colombia, "
        "descargados de la página de GBIF. Los datos corresponden a observaciones reportadas en el año 2024.\n\n"
        "Se incluyen gráficas que muestran tendencias en las 10 familias más predominantes, distribuciones por región, "
        "proporciones significativas y otras características relevantes de las observaciones de aves.\n\n"
        "Las 10 familias con mayor numero de observaciones son: Cathartidae, Accipitridae, Thraupidae,"
        "Tyrannidae, Icteridae, Phoenicopteridae, Psittacidae, Ardeidae, Columbidae, Hirundinidae.\n\n"
        "La mayor cantidad de familias registradas fue en el mes de Junio en el departamento de Casanare.\n\n"
        "En cuanto a la distribución de aves por altitud, podemos concluir que a los 1500-2000 m.s.n.m, sólo"
        "se reportan seis familias. Además las familias Columbidae, Thraupidae, Accipitridae y Tyrannidae se"
        "encuentran en todas las altitudes a lo largo del país.\n\n"
        "Finalmente, se realizó una gráfica con valores reales y aleatorios, con el fin de simular una"
        "comparación de dos conjuntos de registros de aves en el año 2024.\n\n"
        "Los departamentos con mayor diversidad de aves son Antioquia y Cundinamarca. Sin embargo para Arauca, Caquetá y San "
        "Andrés y Providencia no hay datos subidos en GBIF.\n\n"
        "A continuación se muestran las gráficas del análisis de datos:"
    ), fontsize=12, ha='center', wrap=True)

    pdf.savefig()
    plt.close()

    # GRÁFICA 1: Top 10 familias más numerosas en Colombia
    top_10_familias = family_counts.nlargest(10)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_10_familias.index, y=top_10_familias.values, palette='pastel')
    plt.xlabel('Familias de aves')
    plt.ylabel('Conteo de individuos')
    plt.title('Top 10: Familias de Aves con mayor número de individuos')
    plt.tight_layout()
    pdf.savefig()
    plt.close()

    # GRÁFICA 2: Familias de aves por departamento en Colombia
    pivot_table = family_stateProvince.pivot(index='stateProvince', columns='family', values='counts').fillna(0)
    pivot_table.plot(kind='bar', stacked=True, figsize=(14, 8), colormap='tab20')
    plt.title('Distribución de Familias por Región 2024', fontsize=16)
    plt.ylabel('Número de Registros', fontsize=12)
    plt.xlabel('Región de Colombia', fontsize=12)
    plt.xticks(rotation=90, fontsize=10, ha='right')
    plt.legend(title='Familias', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    pdf.savefig()
    plt.close()

    # GRÁFICA 3: Diferencias significativas en la familia más predominante por región
    order_counts = df.groupby(['stateProvince', 'order']).size().reset_index(name='counts')
    predominant_order = order_counts.loc[order_counts.groupby('stateProvince')['counts'].idxmax()]
    total_counts_by_region = df.groupby('stateProvince').size().reset_index(name='total_counts')
    predominant_order = predominant_order.merge(total_counts_by_region, on='stateProvince')
    predominant_order['proportion'] = predominant_order['counts'] / predominant_order['total_counts']
    anova_result = f_oneway(*[group['proportion'].values for _, group in predominant_order.groupby('stateProvince')])
    kruskal_result = kruskal(*[group['proportion'].values for _, group in predominant_order.groupby('stateProvince')])
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=predominant_order, x='stateProvince', y='proportion', hue='stateProvince', palette='pastel')
    plt.title('Proporción del Orden Predominante por departamento')
    plt.ylabel('Proporción del Orden Predominante')
    plt.xlabel('Departamento de Colombia')
    plt.text(0, predominant_order['proportion'].max() + 0.02,
             f"p-valor Kruskal-Wallis: {kruskal_result.pvalue:.4f}", fontsize=9, color='black')
    plt.xticks(rotation=90)
    plt.tight_layout()
    pdf.savefig()
    plt.close()

    # GRÁFICA 4: Número de individuos por familia, mes a mes en el año 2024
    df['eventDate'] = pd.to_datetime(df['eventDate'], errors='coerce')
    df['month'] = df['eventDate'].dt.month
    families_by_region_month = df.groupby(['stateProvince', 'month'])['family'].nunique().reset_index()
    families_by_region_month.rename(columns={'family': 'num_families'}, inplace=True)
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=families_by_region_month, x='month', y='stateProvince', size='num_families',
                    hue='num_families', palette='viridis', sizes=(40, 200), legend='full')
    plt.title('Distribución de familias de aves por departamento en cada mes (2024)', fontsize=12)
    plt.xlabel('Mes del año', fontsize=9)
    plt.ylabel('Departamento de Colombia', fontsize=9)
    plt.xticks(ticks=range(1, 12), labels=['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                                           'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre'], rotation=40)
    plt.legend(title='Número de Familias', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    pdf.savefig()
    plt.close()

    # GRÁFICA 5: Familias por Altitud en Colombia
    df = df.dropna(subset=['elevation'])
    df['elevation'] = pd.to_numeric(df['elevation'], errors='coerce')
    top_10_familias = df.groupby('family')['individualCount'].sum().nlargest(10).index
    df_top_familias = df[df['family'].isin(top_10_familias)]
    plt.figure(figsize=(14, 8))
    sns.scatterplot(data=df_top_familias, x='elevation', y='family', hue='family', palette='tab10', alpha=0.7, s=100)
    plt.title('Distribución de Familias de Aves en Colombia de Acuerdo a la Altitud', fontsize=16)
    plt.xlabel('Altitud (m.s.n.m)', fontsize=12)
    plt.ylabel('Top 10 Familias más Numerosas', fontsize=12)
    plt.legend(title='Familias', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    pdf.savefig()
    plt.close()

    # GRÁFICA 6: Comparación de Valores Reales vs Aleatorios
    real_values = df_top_familias.groupby('family')['individualCount'].sum()
    random_values = real_values.apply(lambda x: np.random.randint(low=x * 0.8, high=x * 1.2))
    comparison_df = pd.DataFrame({'Familia': real_values.index, 'Valores Reales': real_values.values,
                                  'Valores Aleatorios': random_values.values})
    plt.figure(figsize=(12, 6))
    width = 0.5
    x = np.arange(len(comparison_df))
    plt.bar(x - width/2, comparison_df['Valores Reales'], width=width, label='Valores Reales', color='green')
    plt.bar(x + width/2, comparison_df['Valores Aleatorios'], width=width, label='Valores Aleatorios', color='orange')
    plt.title('Comparación de Valores Reales vs. Aleatorios por Familia', fontsize=16)
    plt.xlabel('Familias', fontsize=12)
    plt.ylabel('Número de Individuos', fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    pdf.savefig()
    plt.close()

print(f"El archivo PDF se ha guardado como {pdf_file}")