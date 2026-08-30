# AI Rematch — Version 1 vs Version 2

## Result

The improved prompt produced a stronger and more complete implementation than the first AI attempt.

### Version 1

The first AI version:

- passed Python compilation
- passed 2 pytest tests
- kept the seed at 200 rows after two runs
- generated a real A4 PDF
- generated a 7-page PDF
- implemented the required FastAPI routes
- implemented daily duplicate protection
- used `shop.db`
- used pytest and httpx
- had a very short README

### Version 2

The improved rematch:

- passed Python compilation
- passed 4 pytest tests
- kept the seed at exactly 200 rows after two runs
- generated and inspected a real A4 PDF
- generated a 6-page PDF
- implemented database-level daily idempotency
- used the explicitly requested `report.db`
- documented decisions that were not specified
- used UTC consistently for report dates and timestamps
- used a fixed random seed for reproducible data
- used a unique non-null report date for normal reports
- used NULL for forced reports to bypass the unique daily constraint

## What improved after the prompt was improved?

The biggest improvement was specificity.

The second prompt explicitly required:

- `report.db`
- database-level idempotency
- broader automated test coverage
- pinned dependencies
- configurable test behavior
- complete README documentation
- explicit verification of the generated PDF
- disclosure of decisions that were not specified

Because those requirements were stated directly, the second AI version made fewer silent design decisions and produced stronger verification coverage.

## Concrete V1 vs V2 differences

1. **Test coverage**
   - V1: 2 pytest tests passed.
   - V2: 4 pytest tests passed.

2. **Database naming**
   - V1 silently selected `shop.db`.
   - V2 used the explicitly requested `report.db`.

3. **Idempotency**
   - V1 implemented duplicate protection.
   - V2 was explicitly asked for persistence-level protection and used a unique database field for normal daily reports.

4. **Unspecified decisions**
   - V1 made choices such as the database filename without calling attention to them.
   - V2 explicitly reported decisions such as UTC timestamps, deterministic seeding, and the NULL strategy for forced reports.

5. **Prompt quality**
   - V1 came from a short human-style prompt.
   - V2 came from a more precise prompt based on weaknesses discovered during the first implementation review.

## Conclusion

The rematch showed that the AI implementation improved when the prompt specified behavior that affects correctness, persistence, testing, reproducibility, and documentation.

The first prompt was enough to produce a working application, but the improved prompt reduced ambiguity and produced a more thoroughly tested implementation.
