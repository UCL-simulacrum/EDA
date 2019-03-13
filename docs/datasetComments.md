
1. 179511 patients have a non null `"DEATHCAUSECODE_UNDERLYING"` with a `"NEWVITALSTATUS"` that is not `"D"`.
2. 54161 tumours have a `"SITE_ICD10_O2"`and `"SITE_ICD10_O2_3CHAR"` which don't correspond to eachother
3. When linking `"av_tumour"` with `"sact_tumour"` only 195927 of the 333622 patients have a `"SITE_ICD10_O2"` that is the same as `"PRIMARY_DIAGNOSIS"` (looking at only the first 3 characters)
4. It may be safer to use only the first 3 characters of ICD10 codes in all cases, as the final character associatied with a tumour can change from e.g. C349 (Malignant neoplasm: Bronchus or lung, unspecified) to C341 (Malignant neoplasm: Upper lobe, bronchus or lung)