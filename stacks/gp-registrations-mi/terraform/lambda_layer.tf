resource "aws_lambda_layer_version" "mi_enrichment" {
  filename                 = var.mi_enrichment_lambda_layer_zip
  layer_name               = "${var.environment}_mi_enrichment_layer"
  compatible_runtimes      = ["python3.12"]
  compatible_architectures = ["x86_64"]
  source_code_hash         = filebase64sha256(var.mi_enrichment_lambda_layer_zip)
}
