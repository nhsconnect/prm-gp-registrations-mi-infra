locals {
  common_tags = {
    CreatedBy           = var.repo_name
    Environment         = var.environment
    envtype             = var.environment
    Team                = var.team
    TagVersion          = "1"
    Programme           = "GP IT Futures"
    Project             = "Patient Record Migration"
    Owner               = "Candice Moore"
    CostCentre          = "P0688/04"
    Customer            = "NHS D"
    data_classification = "1"
    DataType            = "None"
    ProjectType         = "Public beta"
    PublicFacing        = "Y"
    ServiceCategory     = "Bronze"
    OnOffPattern        = "AlwaysOn"
    BackupLocal         = "False"
    BackupRemote        = "False"
  }
}
