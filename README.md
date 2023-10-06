# bert_classification_new

## Para realizar el scrapping de las noticias de página 12.
*Solo modificar la parte que esta en negrita*

- Correr el primer script scrap_first_step.py y modificar el directorio donde se van a guardar los URL de las noticias: save_pages_in_dir='**{directorio}**/url_tot' y 
    (target=start_crawler, args=(page_number,  '**{directorio}**/url_tot', ['http://www.pagina12.com.ar/'])). Esto va a guardar los URL de las noticias en el directorio de url_tot.

- Correr el segundo script reader_url_second_step.py y modificar urls_folder_path = '**{directorio}**/url_tot' con el path definido anteriormente y os.path.join('**{directorio}**/pages', prefix).

- Correr el tercer script html_a_text_third_step.py y modificar '**{directorio}**/pages/{category}' y open(f'**{directorio}**/pages/{category}_content_plain/{date_published}{archivo_html}.txt', 'w', encoding='utf-8') as file:

- Correr elcuarto script create_df_pq_fourth_step.py y modificar data_dir='**{directorio}**/pages/' y pq.write_table(pa.Table.from_pandas(my_dataset), '**{directorio}**/articles_df_final.parquet') en donde el resultado será el dataframe *articles_df_final.parquet* .

