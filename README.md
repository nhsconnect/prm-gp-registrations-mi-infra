# prm-gp-registrations-mi-infra

## Setup

These instructions assume you are using:

- [aws-vault](https://github.com/99designs/aws-vault) to validate your AWS credentials.
- [dojo](https://github.com/kudulab/dojo) to provide an execution environment
- [colima](https://github.com/abiosoft/colima) to run the docker dojo images

## Applying terraform

Rolling out terraform against each environment is managed by the GoCD pipeline. If you'd like to test it locally, run the following commands:

1. Enter the container:

`aws-vault exec <profile-name> -- dojo`


2. Invoke terraform locally

```
  ./tasks validate <stack-name> <environment>
  ./tasks plan <stack-name> <environment>
```

The stack name denotes the specific stack you would like to validate.
The environment can be `dev` or `prod`.

To run the formatting, run `./tasks format <stack-name> <environment>`

## Troubleshooting
Error: `Too many command line arguments. Did you mean to use -chdir?`

If you are unable to validate/plan, make sure you doing it inside the dojo container by typing
```
    dojo (then running command inside)
    or
    ./tasks dojo-validate

```

Error: `Error: Error inspecting states in the "s3" backend:
S3 bucket does not exist.`

Try deleting the .terraform and the plans (dev.tfplan/prod.tfplan)


Error: `docker: Cannot connect to the Docker daemon at unix:///Users/jnewman/.colima/docker.sock. Is the docker daemon running?.`

You need to install and start colima:
```
colima start
```
