from libs import login
from flask import request, render_template

def get_metadata(db):
    return {
        "login_state": login.LoginState(db, request.args.get("ticket")),
        "allowed_scores": db.allowed_scores(),
        "dining_halls": db.dining_halls()
    }
    
    
def load_page(template, page_data_module, db, *args, **kwargs):
    if page_data_module.type == "page":
        return render_template(template, metadata=get_metadata(db), page_data=page_data_module.page_data(db, *args, **kwargs))
    elif page_data_module.type == "action":
        return page_data_module.action(db, metadata=get_metadata(db), *args, **kwargs)