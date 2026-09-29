try:
    import _bootstrap
except ImportError:
    pass
import argparse
import pandas as pd
import plotly.express as px
from src.utils.config import IBM, REPORTS
from src.utils.helpers import save_json
from src.attrition.preprocessing import load_data,features,split_data

def run_eda(data=IBM):
    df=load_data(data);train,_,_=split_data(df)
    folder=REPORTS/'eda';folder.mkdir(parents=True,exist_ok=True)
    save_json(folder/'dataset_audit.json',{'rows':len(df),'columns_including_derived_id':len(df.columns),'original_columns':len(df.columns)-1,'missing_values':df.isna().sum().to_dict(),'duplicates':int(df.duplicated().sum()),'column_types':df.dtypes.astype(str).to_dict(),'target_distribution':df.Attrition.value_counts().to_dict(),'constant_columns':[c for c in df if df[c].nunique()==1],'exploratory_scope':'Predictive feature relationships use training split only; full-data audit is descriptive.'})
    X=features(train);X.describe(include='all').to_csv(folder/'train_descriptive_statistics.csv')
    correlation=X.select_dtypes(include='number').corr();correlation.to_csv(folder/'train_correlations.csv')
    px.imshow(correlation,title='Training feature correlations').write_html(folder/'correlations.html',include_plotlyjs='cdn')
    px.histogram(train,x='Attrition',title='Training target distribution').write_html(folder/'attrition_distribution.html',include_plotlyjs='cdn')
    for col in X:
        fig=px.histogram(train,x=col,color='Attrition',barmode='group',title=f'Training distribution: {col}')
        fig.write_html(folder/f'{col}.html',include_plotlyjs='cdn')
    train.assign(Left=train.Attrition.eq('Yes')).groupby('Department').Left.agg(['count','mean']).to_csv(folder/'department_attrition.csv')
    print('EDA saved:',folder)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default=str(IBM));run_eda(p.parse_args().data)
