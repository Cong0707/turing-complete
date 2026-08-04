# k512 execution-input snapshot

This directory preserves the exact six files named by
`K512_INPUT_SHA256SUMS.txt`. The two files later changed for single-target
sharding were reconstructed by reversing only the post-k512 SHA256-filter
patch; every file was then checked byte-for-byte by SHA256 against the original
manifest. The snapshot is evidence-only and is not the current working source.
