# 2026-05-11 Field Health Diagnostic Results

## Test Summary

### News Event Fields (news18 dataset)
| Field | Type | Operators Supported | Result |
|-------|------|-------------------|--------|
| `nws18_qcm` | EVENT (MATRIX) | Cannot use ts_zscore, ts_rank, ts_mean, group_rank | **STOP** - Event inputs not supported |
| `nws18_bam` | EVENT (MATRIX) | Same | **STOP** - Event inputs not supported |
| `nws18_sse` | EVENT (MATRIX) | Same | **STOP** - Event inputs not supported |

**Finding:** News sentiment fields from news18 dataset are EVENT-type matrices. The BRAIN platform does not support time-series operators (ts_zscore, ts_rank, ts_mean, group_rank) on event inputs. These fields cannot be used with standard alpha expression building.

### Social Media Fields (socialmedia12 dataset)
| Field | Type | Coverage | Result |
|-------|------|----------|--------|
| `scl12_buzz_fast_d1` | VECTOR | 0.9756 | ts_rank works but produces no alpha (simulation complete, alphaId=null) |
| `scl12_buzz` | VECTOR | 1.0 | ts_rank works but produces no alpha |
| `scl12_sentiment_fast_d1` | VECTOR | 0.9756 | ts_rank works but produces no alpha |
| `scl12_sentiment` | VECTOR | 1.0 | ts_rank works but produces no alpha |

**Finding:** Social media fields exist and accept ts_rank. However, simulations complete without creating alphas (alphaId=null), suggesting the fields may produce constant/NaN values or have data issues for the TOP3000/USA universe with delay=1.

### Known Working Fields (Verification)
- `close`: Works with ts_rank, creates alpha ✓
- `returns`: Works with ts_rank ✓
- `volume`: Works with ts_rank ✓

## Research Queue Status Update

**Priority 1 (news_sentiment_momentum):** STOPPED - Event fields cannot use time-series operators

**Priority 2 (social_buzz_acceleration):** UNCERTAIN - Fields accept ts_rank but produce no alpha; needs deeper diagnostic

**Priority 3 (model_composite_value_momentum):** NOT YET TESTED

## Recommendation

1. **News sentiment family is unviable** with current field types - the nws18_* fields are EVENT-type and don't support the operators needed for alpha building

2. **Social media family needs different approach** - scl12_* fields exist but may require different expression patterns or have data coverage issues

3. **Consider alternative data sources:**
   - fundamental6 dataset (assets, eps, etc.) - these are known to work
   - model16 dataset (factor scores)
   - sentiment1 dataset fields

## Next Steps
- Wait for API rate limit to clear
- Test fundamental fields (eps, book_to_market, etc.)
- Test sentiment1 fields with VECTOR type (snt1_d1_dynamicfocusrank)