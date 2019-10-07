from libs import login
from flask import request, render_template

def get_metadata(db):
    return {
        "login_state": login.LoginState(request.args.get("ticket")),
        "dining_halls": db.diningHalls()
    }
    
    
def load_page(template, page_data_module, db):
    if page_data_module.type == "page":
        return render_template(template, metadata=get_metadata(db), page_data=page_data_module.page_data(db))
    elif page_data_module.type == "action":
        return page_data_module.action(db)