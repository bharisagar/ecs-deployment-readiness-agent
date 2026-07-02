# AWS Read-only IAM Policy

Use this policy for `aws-readonly` mode. It allows only read operations needed by the readiness agent.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EcsReadinessReadOnly",
      "Effect": "Allow",
      "Action": [
        "ecr:DescribeRepositories",
        "ecr:DescribeImages",
        "ecr:BatchGetImage",
        "logs:DescribeLogGroups",
        "iam:GetRole",
        "iam:ListAttachedRolePolicies",
        "elasticloadbalancing:DescribeTargetGroups",
        "elasticloadbalancing:DescribeTargetHealth",
        "ecs:DescribeTaskDefinition",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

The application does not call create, update, delete, run, register, or put APIs.
