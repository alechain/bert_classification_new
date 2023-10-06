import pandas as pd
import numpy as np
import os
import re
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

data_dir='/Users/achain/Documents/github/bert_classification_new/pages/'

plain_txt=[ data_dir+i for i in os.listdir(data_dir) if i.find('plain')!=-1]

labels = []
texts = []
dates = []
date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')

# Iterate over folders
for folder_path in plain_txt:
    label = os.path.basename(folder_path)  # Extract label from folder name
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            # Extract date using regular expression
            match = date_pattern.search(filename)
            date = match.group(1) if match else None

            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
                text = file.read()

                # If the title starts with "None", assign null date
                if date and not text.startswith("None"):
                    labels.append(label)
                    texts.append(text)
                    dates.append(date)

# Create a DataFrame
my_dataset = pd.DataFrame({'label': labels, 'text': texts, 'date': dates})
my_dataset['label']=my_dataset.label.str.split('_',expand=True).iloc[:,0]

my_dataset.columns=['label', 'sentence', 'date']

# Guardamos el dataframe en parquet file
pq.write_table(pa.Table.from_pandas(my_dataset), '/Users/achain/Documents/github/bert_classification_new/articles_df_final.parquet')
