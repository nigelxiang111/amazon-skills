# Input Validator - 输入验证模块

## 职责
在数据采集前验证所有用户输入，防止无效数据导致API浪费

## 验证规则

### ASIN验证
```python
import re

def validate_asin(asin: str) -> tuple[bool, str]:
    """验证ASIN格式"""
    if not asin:
        return False, "ASIN不能为空"
    
    # ASIN格式: B0开头 + 8位大写字母或数字
    pattern = r'^B0[A-Z0-9]{8}$'
    if not re.match(pattern, asin.upper()):
        return False, f"ASIN格式错误: {asin}，应为B0开头的10位字符"
    
    return True, asin.upper()
```

### 站点验证
```python
VALID_MARKETPLACES = {
    'US', 'UK', 'DE', 'FR', 'ES', 'IT', 'JP', 
    'CA', 'MX', 'AU', 'AE', 'IN', 'BR', 'SA'
}

def validate_marketplace(site: str) -> tuple[bool, str]:
    """验证站点代码"""
    if not site:
        return True, 'US'  # 默认美国站
    
    site_upper = site.upper()
    if site_upper not in VALID_MARKETPLACES:
        return False, f"不支持的站点: {site}，支持: {', '.join(VALID_MARKETPLACES)}"
    
    return True, site_upper
```

### 数值验证
```python
def validate_price(price: float) -> tuple[bool, str]:
    """验证价格范围"""
    if price < 0.01 or price > 9999.99:
        return False, f"价格超出范围: ${price}，应在$0.01-$9999.99之间"
    return True, ""

def validate_weight(weight_kg: float) -> tuple[bool, str]:
    """验证重量范围"""
    if weight_kg < 0.001 or weight_kg > 100:
        return False, f"重量超出范围: {weight_kg}kg，应在0.001-100kg之间"
    return True, ""
```

### 产品名称验证
```python
def validate_product_name(name: str) -> tuple[bool, str]:
    """验证产品名称"""
    if not name or len(name.strip()) < 2:
        return False, "产品名称至少2个字符"
    
    if len(name) > 200:
        return False, "产品名称过长，最多200字符"
    
    return True, name.strip()
```

## 使用方式

在每个模块的Step 1执行验证：

```python
# product_spy模块示例
from core.validator import validate_asin, validate_marketplace

# 验证输入
valid, result = validate_asin(user_asin)
if not valid:
    return f"❌ {result}"

valid, marketplace = validate_marketplace(user_site)
if not valid:
    return f"❌ {result}"

# 继续执行...
```
