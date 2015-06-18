from flask import render_template,  url_for, current_app
from . import myapp
from . import db




import logging
import traceback
logger = logging.getLogger(__name__)


def get_imports_data():

    sql = """

  select  country_name as country,mk_commodity_alpha_all as product,port_name as port,  sum(cast(maf_value as integer)) as quantity
    from imports as i
    left join eightdigitcodes as e
    on i.maf_comcode8 = e.mk_comcode8

    left join countries as c

    on i.maf_coo_alpha = c.alpha_code

    left join ports as p
    on p.alpha_code = i.maf_port_alpha
    where country_name is not null and mk_commodity_alpha_all is not null and port_name is not null and maf_value is not null
    and cast(substr(e.mk_comcode8,1,2) as integer) < 23

    group by country_name, mk_commodity_alpha_all, port_name


    """

    result = db.session.execute(sql)

    return result

def db_result_to_json_in_d3csv_format(dbresult):

    fa = dbresult.fetchall()
    k  = dbresult.keys()

    def to_dict(result_row):
        my_tuples = zip(k,result_row)
        my_dict = dict((x,y) for x,y in my_tuples)
        return my_dict

    final = map(to_dict,fa)
    #final = json.dumps(final)
    return final


@myapp.route('/' ,methods=["GET","POST"])
def home():

    app = current_app._get_current_object()

    logger.info(app.config["SQLALCHEMY_DATABASE_URI"])
    

    return render_template('home.html')

@myapp.route('/imports', methods=["GET","POST"])
def imports_view():

    return render_template('imports.html')









#All json routes are below

from flask import jsonify

@myapp.route('/importsdata.json', methods=["GET","POST"])
def get_imports_json():
    result = get_imports_data()
    result = db_result_to_json_in_d3csv_format(result)


    resp = jsonify(csv_like_data = result)
    resp.status_code = 200

    return resp