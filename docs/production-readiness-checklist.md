# ECS Production Readiness Checklist

- [ ] Image exists
- [ ] Image tag immutable
- [ ] No `latest` tag for production
- [ ] Required env vars configured
- [ ] Secrets stored in Secrets Manager or SSM
- [ ] Health check endpoint available
- [ ] Correct container port
- [ ] CloudWatch log group configured
- [ ] Task CPU/memory valid
- [ ] Task execution role configured
- [ ] Security groups planned
- [ ] ALB target group health path confirmed
- [ ] Rollback image tag available
- [ ] Observability enabled
