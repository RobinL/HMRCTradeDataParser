from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from my_database import Base


class Import(Base):
    __tablename__ = 'imports'

    id = Column(Integer,primary_key = True)
    maf_comcode = Column(String(9))
    maf_sitc = Column(String(5))
    maf_record_type = Column(String(3))
    maf_cod_sequence = Column(String(3))
    maf_cod_alpha = Column(String(2))
    maf_coo_sequence = Column(String(3))
    maf_coo_alpha = Column(String(2), ForeignKey("countries.alpha_code"))
    maf_account_mm = Column(String(2))
    maf_account_ccyy = Column(String(4))
    maf_port_sequence = Column(String(3))
    maf_port_alpha = Column(String(3), ForeignKey("ports.alpha_code"))
    maf_flag_sequence = Column(String(3))
    maf_flag_alpha = Column(String(2))
    maf_country_sequence_coo_imp = Column(String(3))
    maf_country_alpha_coo_imp = Column(String(2))
    maf_trade_indicator = Column(String(1))
    maf_container = Column(String(3))
    maf_mode_of_transport = Column(String(3))
    maf_inland_mot = Column(String(2))
    maf_golo_sequence = Column(String(3))
    maf_golo_alpha = Column(String(3))
    maf_suite_indicator = Column(String(3))
    maf_procedure_code = Column(String(3))
    maf_cb_code = Column(String(3))
    maf_value = Column(String(16))
    maf_quantity_1 = Column(String(14))
    maf_quantity_2 = Column(String(14))

    #Not part of file spec but enables easier joins
    maf_comcode8 = Column(String(8), ForeignKey("eightdigitcodes.mk_comcode8"))


    #Establish this as linked to the comcode table.
    comcode = relationship("EightDigitCode")
    country = relationship("Country")
    port = relationship("Port")


class ImportHeader(Base):
    __tablename__ = 'importsheaders'

    id = Column(Integer,primary_key = True)

    maf_file_name = Column(String(22))
    maf_month_alpha = Column(String(9))
    maf_suite = Column(String(18))
    maf_year = Column(String(4))


class EightDigitCodeHeader(Base):
    __tablename__ = "eightdigitcodesheaders"

    id = Column(Integer,primary_key = True)

    mk_filename = Column(String(22))
    mk_month = Column(String(2))
    mk_year = Column(String(4))

class EightDigitCode(Base):
    __tablename__ = "eightdigitcodes"

    id = Column(Integer,primary_key = True)
    mk_comcode = Column(String(9))
    mk_intra_extra_ind = Column(String(1))
    mk_intra_mm_on = Column(String(2))
    mk_intra_yy_on = Column(String(2))
    mk_intra_mm_off = Column(String(2))
    mk_intra_yy_off = Column(String(2))
    mk_extra_mm_on = Column(String(2))
    mk_extra_yy_on = Column(String(2))
    mk_extra_mm_off = Column(String(2))
    mk_extra_yy_off = Column(String(2))
    mk_non_trade_id = Column(String(1))
    mk_sitc_no = Column(String(5))
    mk_sitc_ind = Column(String(1))
    mk_sitc_conv_a = Column(String(3))
    mk_sitc_conv_b = Column(String(3))
    mk_cn_q2 = Column(String(3))
    mk_supp_arrivals = Column(String(2))
    mk_supp_despatches = Column(String(2))
    mk_supp_imports = Column(String(2))
    mk_supp_exports = Column(String(2))
    mk_sub_group_arr = Column(String(1))
    mk_item_arr = Column(String(1))
    mk_sub_group_desp = Column(String(1))
    mk_item_desp = Column(String(1))
    mk_sub_group_imp = Column(String(1))
    mk_item_imp = Column(String(1))
    mk_sub_group_exp = Column(String(1))
    mk_item_exp = Column(String(1))
    mk_qty1_alpha = Column(String(3))
    mk_qty2_alpha = Column(String(3))
    mk_commodity_alpha_1 = Column(String(61))
    mk_commodity_alpha_2 = Column(String(48))
    mk_commodity_alpha_all = Column(String(4906))

    #Not part of spec but makes for easier joins
    mk_comcode8 = Column(String(8), index=True)

    #We want to be able to pick up importers from a code if they exist
    importers = relationship("ImporterEightDigitCodes")


class OtherDigitCodes(Base):
    __tablename__ = "otherdigitcodes"

    id = Column(Integer, primary_key=True)

class ImporterHeader(Base):
    __tablename__ = "importersheaders"

    id = Column(Integer,primary_key = True)

    ia_record_type = Column(String(2))
    ia_runno = Column(String(5))
    ia_year = Column(String(4))


class Importer(Base):
    __tablename__ = "importers"

    id = Column(Integer,primary_key = True)

    ia_record_type = Column(String(2))
    ia_name = Column(String(105), index=True)
    ia_addr_1 = Column(String(30), index=True)
    ia_addr_2 = Column(String(30), index=True)
    ia_addr_3 = Column(String(30), index=True)
    ia_addr_4 = Column(String(30), index=True)
    ia_addr_5 = Column(String(30), index=True)
    ia_pcode = Column(String(8), index=True)
    # ia_comcode_count = Column(String(3))
    # ia_comcode = Column(String(4235))


    comcodes = relationship("ImporterEightDigitCodes",cascade="delete")


class ImporterEightDigitCodes(Base):
    __tablename__  = "importerseightdigitcodes"

    id = Column(Integer, primary_key=True)

    #Establish this as linked to the comcode table.
    comcode8 = Column(String(8), ForeignKey("eightdigitcodes.mk_comcode8"))
    comcode = relationship("EightDigitCode")

    month_of_import = Column(Integer)
    year_of_import = Column(Integer)


    #Establish
    importer_id = Column(Integer, ForeignKey("importers.id"))
    impoter = relationship("Importer")


class MetaData(Base):
    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True)
    field_name = Column(String(100))
    full_name = Column(String(200))
    description =  Column(String(2000))

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    country_name = Column(String(140))
    alpha_code = Column(String(3))
    sequence_code = Column(Integer)
    comments = Column(String(400))

    imports = relationship("Import")

class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True)
    port_name = Column(String(140))
    alpha_code = Column(String(3))
    sequence_code = Column(Integer)

class RawFileLog(Base):
    __tablename__ = "rawfiles"

    id = Column(Integer, primary_key=True)
    file_name = Column(String(40))
    url = Column(String(120))








