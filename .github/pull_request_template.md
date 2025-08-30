# 🚀 BNB Trading System - Pull Request Template

## 📊 PR Type & Category
<!-- Select the appropriate category -->
- [ ] **Phase Foundation** - Core infrastructure & cleanup
- [ ] **Signal Enhancement** - LONG/SHORT signal accuracy improvements
- [ ] **Market Intelligence** - Smart filtering & regime detection
- [ ] **Testing Framework** - Performance validation & backtesting
- [ ] **Bug Fix** - Critical error resolution
- [ ] **Documentation** - Updates to CLAUDE.md, MODULES.md, TODO.md

## 🎯 Summary
<!-- Provide a clear, concise summary of what this PR accomplishes -->

### Key Components
<!-- List the main files/modules being modified -->
- **Modified Files**:
- **New Features**:
- **Bug Fixes**:
- **Performance Impact**:

## 📈 Performance Impact
<!-- Include backtesting results if applicable -->

### Before & After Metrics
- **Overall Accuracy**: X% → Y% (target: 59.7%+)
- **LONG Accuracy**: X% → Y% (target: 85%+)
- **SHORT Accuracy**: X% → Y% (target: 75%+)
- **Average P&L**: X% → Y% per signal

### Backtesting Results
<!-- Paste relevant backtest results -->
```
Backtest Period: YYYY-MM-DD to YYYY-MM-DD
Total Signals: X (Y LONG, Z SHORT)
Performance metrics...
```

## 🔧 Technical Changes

### Core Module Updates
<!-- List significant changes to core modules -->
- **signal_generator.py**:
- **trend_analyzer.py**:
- **smart_short_generator.py**:
- **config.toml**:

### New Features
<!-- Describe new functionality -->
- [ ] Market regime detection enhancements
- [ ] Enhanced signal confluence requirements
- [ ] Improved risk management filters
- [ ] Multi-timeframe coordination improvements

### Bug Fixes
<!-- List any bugs being resolved -->
- [ ] Fixed: [describe bug]
- [ ] Resolved: [describe issue]

## 🧪 Testing & Validation

### Testing Completed
- [ ] **18-month backtesting** completed with new changes
- [ ] **Signal validation** against historical data
- [ ] **Configuration validation** for all parameters
- [ ] **Error handling** tested for edge cases
- [ ] **Integration testing** with all modules

### Quality Assurance
- [ ] **Code review** completed
- [ ] **Type hints** added/updated where needed
- [ ] **Error handling** comprehensive
- [ ] **Logging** appropriate for debugging
- [ ] **Documentation** updated (CLAUDE.md, MODULES.md)

## 📋 Configuration Changes

### config.toml Updates
<!-- List any configuration parameter changes -->
```toml
[section]
parameter = new_value  # Description of change
```

### Impact on Existing Settings
- [ ] **Backward compatible** - no breaking changes
- [ ] **Migration required** - existing users need to update config
- [ ] **New parameters added** - with sensible defaults

## 🎯 Success Criteria

### Performance Targets
- [ ] Overall accuracy maintained/improved (>59.7%)
- [ ] LONG accuracy progress toward 85% target
- [ ] SHORT accuracy progress toward 75% target
- [ ] No performance regression in backtesting

### Code Quality
- [ ] All modules pass validation
- [ ] Error handling robust
- [ ] Documentation complete
- [ ] Configuration validated

## 🔍 Risk Assessment

### Potential Risks
<!-- Identify any potential risks -->
- [ ] **Low Risk** - Minor improvements, no breaking changes
- [ ] **Medium Risk** - Significant logic changes, comprehensive testing completed
- [ ] **High Risk** - Major architectural changes, extensive validation required

### Mitigation Strategies
<!-- How are risks being addressed -->
- Comprehensive backtesting validation
- Gradual rollout approach
- Monitoring and rollback plan

## 📚 Documentation Updates

### Files Updated
- [ ] **CLAUDE.md** - System overview and commands
- [ ] **MODULES.md** - Technical documentation
- [ ] **TODO.md** - Development priorities
- [ ] **README.md** - User-facing documentation

### Documentation Quality
- [ ] **Performance metrics** updated with latest results
- [ ] **Code references** updated with line numbers
- [ ] **Configuration examples** reflect current parameters
- [ ] **Usage examples** tested and validated

## 🤖 Automated Checks

### Pre-merge Requirements
- [ ] **All tests pass** - backtesting validation successful
- [ ] **Configuration valid** - config.toml syntax correct
- [ ] **Documentation current** - all files synchronized
- [ ] **Performance validated** - no accuracy regression

---

## 🎯 Expected Outcomes

### Immediate Benefits
<!-- What this PR accomplishes immediately -->

### Long-term Impact
<!-- How this contributes to overall system goals -->

### Next Steps
<!-- What should be done after this PR is merged -->

---

**🔗 Related Issues**: #issue_number
**📋 Checklist**: All items above completed before requesting review
**🤖 Generated with**: Claude Code - BNB Trading System Enhancement

---

<!--
PR Template Guidelines:
1. Fill out ALL relevant sections
2. Include backtesting results for performance changes
3. Update documentation before submitting
4. Ensure comprehensive testing completed
5. Follow the success criteria checklist
-->
