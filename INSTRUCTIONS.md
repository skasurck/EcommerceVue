# Instructions to update the categories

The category tree has been updated to have a maximum depth of 3 levels.
To apply these changes to the database, please run the following command from the root of the project:

## For Linux/macOS:

```bash
source .venv/Scripts/activate
python backend/manage.py reset_categories
```

## For Windows:

```powershell
.venv\Scripts\activate
python backend\manage.py reset_categories
```
