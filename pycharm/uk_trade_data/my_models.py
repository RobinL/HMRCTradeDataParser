from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean, BigInteger
from sqlalchemy.orm import relationship
from my_database import Base


"""
Note:

The lines which are commented out can be considered 'switches'
If you want to include that column in your tables, just uncomment them

Rerun the code, building the database from scratch and 
these columns will magically appear and be correctly populated

"""

class Import_Estimate(Base):
    __tablename__ = 'import_estimates'

    id = Column(Integer, primary_key=True)
    sitc_2 = Column(String(2), index=True)
    sitc_0 = Column(String(1), index=True)
    month_ind = Column(String(6))
    # estimated_value = Column(String(15))

    source_file_id = Column(Integer, ForeignKey("rawfiles.id",ondelete="cascade"))
    estimated_value_int = Column(BigInteger())
    

    rawfile = relationship("RawFileLog")

class Export_Estimate(Base):
    __tablename__ = 'export_estimates'

    id = Column(Integer, primary_key=True)
    sitc_2 = Column(String(2), index=True)
    sitc_0 = Column(String(1), index=True)
    month_ind = Column(String(6))
    # estimated_value = Column(String(15))

    source_file_id = Column(Integer, ForeignKey("rawfiles.id",ondelete="cascade"))
    estimated_value_int = Column(BigInteger())
    
    rawfile = relationship("RawFileLog")



class Import(Base):
    __tablename__ = 'imports'

    id = Column(Integer,primary_key = True)
    maf_comcode = Column(String(9))
    # maf_sitc = Column(String(5))  #aggregation indicator
    maf_record_type = Column(String(3)) #supression indicator
    # maf_cod_sequence = Column(String(3))
    maf_cod_alpha = Column(String(2))
    # maf_coo_sequence = Column(String(3))
    # maf_coo_alpha = Column(String(2), index=True)
    maf_account_mm = Column(String(2), index=True)
    maf_account_ccyy = Column(String(4),index=True)
    # maf_port_sequence = Column(String(3))
    maf_port_alpha = Column(String(3), index=True)
    # maf_flag_sequence = Column(String(3))
    # maf_flag_alpha = Column(String(2))
    # maf_country_sequence_coo_imp = Column(String(3))
    # maf_country_alpha_coo_imp = Column(String(2))
    maf_trade_indicator = Column(String(1))
    # maf_container = Column(String(3))
    maf_mode_of_transport = Column(String(3))
    # maf_inland_mot = Column(String(2))
    # maf_golo_sequence = Column(String(3))
    # maf_golo_alpha = Column(String(3))
    # maf_suite_indicator = Column(String(3))
    # maf_procedure_code = Column(String(3))
    # maf_cb_code = Column(String(3))
    # maf_value = Column(String(16))
    # maf_quantity_1 = Column(String(14))
    # maf_quantity_2 = Column(String(14))
    source_file_id = Column(Integer, ForeignKey("rawfiles.id",ondelete="cascade"))

    #Not part of file spec but enables easier joins
    #maf_comcode8 = Column(String(8), ForeignKey("eightdigitcodes.mk_comcode8"))
    comcode8 = Column(String(8), index=True)
    maf_value_int = Column(BigInteger())
    maf_quantity_1_int = Column(BigInteger())
    maf_quantity_2_int = Column(BigInteger())


    rawfile = relationship("RawFileLog")


class Export(Base):
    __tablename__ = 'exports'

    id = Column(Integer,primary_key = True)

    maf_comcode = Column(String(9))
    # maf_sitc = Column(String(5))
    maf_record_type = Column(String(3))
    # maf_cod_sequence = Column(String(3))
    maf_cod_alpha = Column(String(2))
    maf_account_mm = Column(String(2))
    # maf_date_delimiter = Column(String(1))
    maf_account_ccyy = Column(String(4))
    # maf_port_sequence = Column(String(3))
    maf_port_alpha = Column(String(3))
    # maf_flag_sequence = Column(String(3))
    # maf_flag_alpha = Column(String(2))
    maf_trade_indicator = Column(String(1))
    # maf_container = Column(String(3))
    maf_mode_of_transport = Column(String(3))
    # maf_inland_mot = Column(String(2))
    # maf_golo_sequence = Column(String(3))
    # maf_golo_alpha = Column(String(3))
    # maf_suite_indicator = Column(String(3))
    # maf_procedure_code = Column(String(3))
    # maf_value = Column(String(6))
    # maf_quantity_1 = Column(String(4))
    # maf_quantity_2 = Column(String(4))
    # maf_industrial_plant_comcode = Column(String(5))


    source_file_id = Column(Integer, ForeignKey("rawfiles.id",ondelete="cascade"))

    #Not part of file spec but enables easier joins
    #maf_comcode8 = Column(String(8), ForeignKey("eightdigitcodes.mk_comcode8"))
    comcode8 = Column(String(8), index=True)
    maf_value_int = Column(BigInteger())
    maf_quantity_1_int = Column(BigInteger())
    maf_quantity_2_int = Column(BigInteger())




class Import_EU(Base):
    __tablename__ = 'eu_imports'

    id = Column(Integer,primary_key = True)
    # smk_comcode = Column(String(9))
    smk_record_type = Column(String(1))
    # smk_cod_seq = Column(String(3))
    smk_cod_alpha = Column(String(2), index=True)
    smk_trade_ind = Column(String(1))
    # smk_coo_seq = Column(String(3))
    # smk_coo_alpha = Column(String(2))  #This is blank in the data anyway
    smk_nature_of_transaction = Column(String(3))
    smk_mode_of_transport = Column(String(3))
    # smk_period_reference = Column(String(7))
    smk_suite_indicator = Column(String(3))
    smk_sitc = Column(String(5))
    # smk_ip_comcode = Column(String(9))
    # smk_no_of_consignments   = Column(String(2))
    # smk_stat_value   = Column(String(6))
    # smk_nett_mass    = Column(String(4))
    # smk_supp_unit    = Column(String(4))

    comcode8 = Column(String(8), index=True)
    smk_no_of_consignments_int   = Column(Integer())
    smk_stat_value_int   = Column(BigInteger())
    smk_nett_mass_int    = Column(BigInteger())
    smk_supp_unit_int    = Column(Integer())
    smk_period_reference_month = Column(String(2),index=True)
    smk_period_reference_year = Column(String(4),index=True)

    source_file_id = Column(Integer, ForeignKey("rawfiles.id", ondelete='cascade'))
    rawfile = relationship("RawFileLog")

class Export_EU(Base):
    __tablename__ = 'eu_exports'

    id = Column(Integer,primary_key = True)

    #smk_comcode = Column(String(9))
    smk_record_type = Column(String(1))
    # smk_cod_seq = Column(String(3))
    smk_cod_alpha = Column(String(2), index=True)
    smk_trade_ind = Column(String(1))
    #smk_coo_seq = Column(String(3))
    smk_coo_alpha = Column(String(2))
    smk_nature_of_transaction = Column(String(3))
    smk_mode_of_transport = Column(String(3))
    #smk_period_reference = Column(String(7))
    smk_suite_indicator = Column(String(3))
    smk_sitc = Column(String(5))
    #smk_ip_comcode = Column(String(9))
    #smk_no_of_consignments = Column(String(12))
    #smk_stat_value = Column(String(16))
    #smk_nett_mass = Column(String(14))
    #smk_supp_unit = Column(String(14))

    comcode8 = Column(String(8), index=True)
    smk_stat_value_int   = Column(BigInteger())
    smk_nett_mass_int    = Column(BigInteger())
    smk_period_reference_month = Column(String(2),index=True)
    smk_period_reference_year = Column(String(4),index=True)

    source_file_id = Column(Integer, ForeignKey("rawfiles.id", ondelete='cascade'))
    rawfile = relationship("RawFileLog")


class EightDigitCode(Base):
    __tablename__ = "eightdigitcodes"

    id = Column(Integer,primary_key = True)
    # mk_comcode = Column(String(9))
    # mk_intra_extra_ind = Column(String(1))
    # mk_intra_mm_on = Column(String(2))
    # mk_intra_yy_on = Column(String(2))
    mk_intra_mm_off = Column(String(2))
    mk_intra_yy_off = Column(String(2))
    # mk_extra_mm_on = Column(String(2))
    # mk_extra_yy_on = Column(String(2))
    mk_extra_mm_off = Column(String(2))
    mk_extra_yy_off = Column(String(2))
    # mk_non_trade_id = Column(String(1))
    mk_sitc_no = Column(String(5))
    mk_sitc_ind = Column(String(1))
    mk_sitc_conv_a = Column(String(3))
    mk_sitc_conv_b = Column(String(3))
    # mk_cn_q2 = Column(String(3))
    # mk_supp_arrivals = Column(String(2))
    # mk_supp_despatches = Column(String(2))
    # mk_supp_imports = Column(String(2))
    # mk_supp_exports = Column(String(2))
    # mk_sub_group_arr = Column(String(1))
    # mk_item_arr = Column(String(1))
    # mk_sub_group_desp = Column(String(1))
    # mk_item_desp = Column(String(1))
    # mk_sub_group_imp = Column(String(1))
    # mk_item_imp = Column(String(1))
    # mk_sub_group_exp = Column(String(1))
    # mk_item_exp = Column(String(1))
    # mk_qty1_alpha = Column(String(3))
    # mk_qty2_alpha = Column(String(3))
    # mk_commodity_alpha_1 = Column(String(61))
    # mk_commodity_alpha_2 = Column(String(48))
    mk_commodity_alpha_all = Column(String(4906))

    #Not part of spec but makes for easier joins
    mk_comcode8 = Column(String(8), index=True,unique=True)
    source_file_id = Column(Integer, ForeignKey("rawfiles.id"))
    rawfile = relationship("RawFileLog")

    #We want to be able to pick up importers from a code if they exist
    #importers = relationship("ImporterEightDigitCodes")

#
# class CombinedNomenclature(Base):
#     __tablename__ = "combined_nomenclature"
#
#     id = Column(Integer, primary_key=True)
#     commodity_code_8 = Column(String(8),index=True,unique=True)
#     commodity_code_8_desc = Column(String(2000))
#     combined_nomenclature_6 = Column(String(6), index=True)
#     combined_nomenclature_6_desc = Column(String(2000))
#     combined_nomenclature_4 = Column(String(4), index=True)
#     combined_nomenclature_4_desc = Column(String(2000))
#     combined_nomenclature_2 = Column(String(2), index=True)
#     combined_nomenclature_2_desc = Column(String(2000))
#     combined_nomenclature_1 = Column(String(2), index=True)
#     combined_nomenclature_1_desc = Column(String(2000))


class Importer(Base):
    __tablename__ = "importers"

    id = Column(Integer,primary_key = True)

    ia_record_type = Column(String(2))
    ia_name = Column(String(105))
    ia_addr_1 = Column(String(30))
    ia_addr_2 = Column(String(30))
    ia_addr_3 = Column(String(30))
    ia_addr_4 = Column(String(30))
    ia_addr_5 = Column(String(30))
    ia_pcode = Column(String(8))

    #This is not in the original files from hmrc
    importer_hash = Column(String(56), index=True)
    postcode_nospace = Column(String(8), index=True)

    source_file_id = Column(Integer,ForeignKey("rawfiles.id", ondelete='cascade'))
    rawfile = relationship("RawFileLog")



class ImporterEightDigitCodes(Base):
    __tablename__  = "importerseightdigitcodes"

    id = Column(Integer, primary_key=True)

    #Establish this as linked to the comcode table.
    comcode8 = Column(String(8), index=True)

    month_of_import = Column(String(2),index=True)
    year_of_import = Column(String(4), index=True)

    source_file_id = Column(Integer, ForeignKey("rawfiles.id", ondelete='cascade'))
    rawfile = relationship("RawFileLog")

    importer_id = Column(Integer, ForeignKey("importers.id", ondelete='cascade'))
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
    alpha_code = Column(String(2),unique=True)
    sequence_code = Column(Integer)
    comments = Column(String(400))

    #imports = relationship("Import")

class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True)
    port_name = Column(String(140))
    alpha_code = Column(String(3),unique=True)
    sequence_code = Column(Integer)

class RawFileLog(Base):
    __tablename__ = "rawfiles"

    id = Column(Integer, primary_key=True)
    file_type = Column(String(50))
    parent_zip_file = Column(String(50))
    child_zip_file = Column(String(50))
    expected_file_name_in_child_zip = Column(String(50))
    actual_file_name_in_child_zip = Column(String(50))
    url = Column(String(120))
    processing_completed = Column(Boolean)
    timestamp = Column(String(120))
    month = Column(Integer())
    year = Column(Integer())

    imports = relationship("Import", cascade="all,delete, delete-orphan", passive_deletes=True,backref="rawfiles")
    exports = relationship("Export", cascade="all,delete",passive_deletes=True)
    importers = relationship("Importer", cascade="all,delete, delete-orphan",passive_deletes=True)
    importers_codes = relationship("ImporterEightDigitCodes", cascade="all,delete,delete-orphan", passive_deletes=True)
    imports_eu = relationship("Import_EU", cascade="all,delete, delete-orphan",passive_deletes=True)
    exports_eu = relationship("Export_EU", cascade="all,delete, delete-orphan",passive_deletes=True)


class Postcode(Base):
    __tablename__ = "postcodes"

    id = Column(Integer, primary_key=True)
    postcode = Column(String(8), index=True)
    lat = Column(Float())
    lng = Column(Float())


class Lookup_Code_1(Base):
    __tablename__ = "lookup_codes_1"

    id = Column(Integer, primary_key=True)
    code_2 = Column(String(2), index=True)
    code = Column(String(2), index=True)
    desc = Column(String(500))
    code_base = Column(String(2))   
    desc_base = Column(String(500))


class Lookup_Code_2(Base):
    __tablename__ = "lookup_codes_2"

    id = Column(Integer, primary_key=True)
    code = Column(String(2), index=True)
    desc = Column(String(500))

class Lookup_Code_4(Base):
    __tablename__ = "lookup_codes_4"

    id = Column(Integer, primary_key=True)
    code = Column(String(2), index=True)
    desc = Column(String(500))

class Lookup_Code_6(Base):
    __tablename__ = "lookup_codes_6"

    id = Column(Integer, primary_key=True)
    code = Column(String(2), index=True)
    desc = Column(String(500))