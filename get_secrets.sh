#!/bin/bash
export VAULT_ADDR=VAULT_URL
# Function to retrieve a secret from Vault and export it as an environment variable
get_secret() {
  local secret_path=$1
  local secret_key=$2
  local env_var_name=$3

  secret_value=$(vault kv get -field=$secret_key $secret_path)
  export $env_var_name=$secret_value

  # Print the environment variable to the console for debugging
  #echo $env_var_name, $secret_value

  # Append the environment variable to the .env file
  echo "$env_var_name=$secret_value" >> .env
}

# Retrieve and export secrets for the prod environment
get_secret path username ENV_USERNAME



