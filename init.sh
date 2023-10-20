#!/bin/bash

url="http://static.decontextualize.com/gutenberg-dammit-files-v002.zip"
catalog_url="https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv"
destination_dir="./books"
unziped_folder="gutenberg-dammit-files"

curl -o ./downloaded.zip "$url"
curl -o pg_catalog.csv "$catalog_url"
unzip -qq ./downloaded.zip
mv "$unziped_folder" "$destination_dir"
rm ./downloaded.zip

base_dir="./books"  # Make sure to use double quotes around variables
for folder in "$base_dir"/*/; do
    folder_name=$(basename "$folder")
    last_three_digits="${folder_name: -3}"  

    for ((i=0; i<=99; i++)); do
        file_num=$(printf "%02d" "$i")
        file_path="$folder$last_three_digits$file_num.txt"
        
        if [ ! -f "$file_path" ]; then
            touch "$file_path"
            # echo "Created $file_path"
        fi
    done
done

echo "running python extraction script"
poetry run python3 extract.py
rm pg_catalog.csv