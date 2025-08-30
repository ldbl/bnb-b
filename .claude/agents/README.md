# BNB Trading System - Specialized Agents

This directory contains specialized Claude Code agents for different aspects of the BNB trading system.

## Available Agents

### 🎯 Trading Expert (`@trading-expert`)

**Focus**: Trading signals, market analysis, 100% LONG accuracy maintenance

-   Analyzes BNB signals and patterns
-   Maintains perfect LONG accuracy standard
-   Provides market regime insights
-   Risk management focus

**Use Cases**:

-   "Should we go LONG now?"
-   "Analyze current market conditions"
-   "Review signal confidence levels"

### 🏗️ Code Architect (`@code-architect`)

**Model**: **Claude Opus** (maximum reasoning for complex architecture)
**Focus**: System architecture, code quality, modular design

-   Designs clean, modular components
-   Ensures type safety and SOLID principles
-   Implements ModuleResult patterns
-   Maintains 0 linting errors

**Use Cases**:

-   "Design new analyzer module"
-   "Improve code architecture"
-   "Fix type safety issues"

### 🧪 Test Engineer (`@test-engineer`)

**Focus**: Comprehensive testing, regression validation

-   Creates unit and integration tests
-   Validates system behavior
-   Ensures 100% LONG accuracy regression
-   Real data testing strategies

**Use Cases**:

-   "Create tests for new module"
-   "Validate system regression"
-   "Design test strategy"

### 📊 Data Analyst (`@data-analyst`)

**Focus**: Market data analysis, performance insights

-   Analyzes historical performance
-   Market pattern recognition
-   Data quality validation
-   Performance metrics tracking

**Use Cases**:

-   "Analyze recent performance"
-   "Validate data quality"
-   "Generate market insights"

## Usage Examples

```bash
# Trading decisions
@trading-expert "Current BNB is at $620, weekly tail shows long wick. LONG signal?"

# Architecture improvements
@code-architect "How to implement new moving average analyzer with ModuleResult?"

# Testing strategy
@test-engineer "Create comprehensive tests for fibonacci analyzer"

# Data insights
@data-analyst "Analyze last 30 signals performance and market conditions"
```

## Agent Collaboration

Agents can work together on complex tasks:

1. **@data-analyst** identifies patterns
2. **@trading-expert** evaluates signal quality
3. **@code-architect** designs implementation
4. **@test-engineer** creates validation strategy

## Model Configuration

Agents are optimized with specific Claude models:

-   **Trading Expert**: Sonnet (balanced speed/quality for analysis)
-   **Code Architect**: **Opus** (maximum reasoning for complex architecture)
-   **Test Engineer**: Sonnet (efficient test generation)
-   **Data Analyst**: Sonnet (fast data processing and insights)

## Configuration

Each agent is configured with:

-   **Context**: System knowledge and current status
-   **Model**: Optimal Claude version for the task
-   **Role**: Specific responsibilities and focus areas
-   **Standards**: Code quality, accuracy, and architectural principles
-   **Tools**: Relevant commands and validation methods
-   **Priorities**: Quality over quantity, risk management first

This ensures consistent, high-quality assistance across all aspects of the trading system.
