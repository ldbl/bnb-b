#!/bin/bash
echo '=== Testing Commit 50d5636 (Working) ==='
git checkout 50d5636 > /dev/null 2>&1
python3 run_enhanced_backtest.py 2>/dev/null | grep -E 'LONG Signals:|Accuracy:'

echo ''
echo '=== Testing Current Main (Broken) ==='
git checkout main > /dev/null 2>&1
python3 run_enhanced_backtest.py 2>/dev/null | grep -E 'LONG Signals:|Accuracy:'

echo ''
echo '=== Back to Recovery Branch ==='
git checkout recovery/restore-21-signals > /dev/null 2>&1
