# poetry run python -m ballerz.update_listings && \
# git add ballerz/ballerz_listing_history.csv && \
poetry run python -m ballerz.update_sales && \
git add ballerz/ballerz_sales_history.csv && \
git commit -m "Update history" && \
git push
