#!/usr/bin/env python3
"""
🧮 CALCULATOR TOOL - SARA's Math Capabilities
Teaches SARA how to do calculations and math operations
"""

import re
import math
from typing import Dict, Optional, Tuple

class CalculatorTool:
    """
    Calculator tool for SARA
    Handles basic math, scientific calculations, unit conversions
    """
    
    def __init__(self):
        self.history = []
        
    def calculate(self, expression: str) -> Dict:
        """
        Safely evaluate a math expression
        
        Args:
            expression: Math expression like "5 + 3", "10 * 2", "sqrt(16)"
        
        Returns:
            Dict with result or error
        """
        result = {
            "status": "error",
            "expression": expression,
            "result": None,
            "formatted": None,
            "error": None
        }
        
        try:
            # Clean the expression
            expr = expression.strip()
            
            # Extract just the math part if embedded in text
            # Handle patterns like "what is 5 plus 3" or "calculate 10 times 2"
            expr = self._extract_math_expression(expr)
            
            if not expr:
                result["error"] = "No math expression found"
                return result
            
            # Sanitize - only allow safe operations
            # Replace words with operators
            expr = self._normalize_expression(expr)
            
            # Safe evaluation with limited namespace
            safe_dict = {
                'abs': abs,
                'max': max,
                'min': min,
                'sum': sum,
                'pow': pow,
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'pi': math.pi,
                'e': math.e,
                'log': math.log,
                'log10': math.log10,
                'exp': math.exp,
                'floor': math.floor,
                'ceil': math.ceil,
                'round': round
            }
            
            # Evaluate
            answer = eval(expr, {"__builtins__": {}}, safe_dict)
            
            result["status"] = "success"
            result["result"] = answer
            
            # Format nicely
            if isinstance(answer, float):
                if answer.is_integer():
                    result["formatted"] = str(int(answer))
                else:
                    result["formatted"] = f"{answer:.6f}".rstrip('0').rstrip('.')
            else:
                result["formatted"] = str(answer)
            
            # Add to history
            self.history.append({
                "expression": expression,
                "result": answer,
                "timestamp": None  # Would need datetime import
            })
            
        except ZeroDivisionError:
            result["error"] = "Cannot divide by zero!"
        except SyntaxError:
            result["error"] = "Invalid math expression"
        except Exception as e:
            result["error"] = f"Math error: {str(e)}"
        
        return result
    
    def _extract_math_expression(self, text: str) -> str:
        """Extract math expression from natural language"""
        text = text.lower()
        
        # Remove common phrases
        prefixes = [
            "what is", "what's", "calculate", "compute", "solve",
            "how much is", "find", "what equals", "equals",
            "can you calculate", "do the math", "math"
        ]
        
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Remove trailing punctuation
        text = text.rstrip('?.!')
        
        return text.strip()
    
    def _normalize_expression(self, expr: str) -> str:
        """Convert natural language to math operators"""
        replacements = [
            # Words to operators
            (r'\bplus\b', '+'),
            (r'\bminus\b', '-'),
            (r'\btimes\b', '*'),
            (r'\bmultiplied by\b', '*'),
            (r'\bdivided by\b', '/'),
            (r'\bdividedby\b', '/'),
            (r'\bover\b', '/'),
            (r'\bsquared\b', '**2'),
            (r'\bcubed\b', '**3'),
            (r'\bto the power of\b', '**'),
            (r'\braised to\b', '**'),
            (r'\bmod\b', '%'),
            (r'\bmodulo\b', '%'),
            # Symbols
            (r'×', '*'),
            (r'÷', '/'),
            (r'[xX]', '*'),
        ]
        
        for pattern, replacement in replacements:
            expr = re.sub(pattern, replacement, expr, flags=re.IGNORECASE)
        
        return expr
    
    def convert_units(self, value: float, from_unit: str, to_unit: str) -> Dict:
        """
        Convert between units
        
        Supports: length, weight, temperature, storage
        """
        result = {
            "status": "error",
            "value": value,
            "from": from_unit,
            "to": to_unit,
            "result": None
        }
        
        try:
            # Length conversions
            length_units = {
                'm': 1, 'meter': 1, 'meters': 1,
                'km': 1000, 'kilometer': 1000, 'kilometers': 1000,
                'cm': 0.01, 'centimeter': 0.01, 'centimeters': 0.01,
                'mm': 0.001, 'millimeter': 0.001, 'millimeters': 0.001,
                'ft': 0.3048, 'foot': 0.3048, 'feet': 0.3048,
                'in': 0.0254, 'inch': 0.0254, 'inches': 0.0254,
                'mi': 1609.344, 'mile': 1609.344, 'miles': 1609.344,
                'yd': 0.9144, 'yard': 0.9144, 'yards': 0.9144
            }
            
            # Weight conversions
            weight_units = {
                'kg': 1, 'kilogram': 1, 'kilograms': 1,
                'g': 0.001, 'gram': 0.001, 'grams': 0.001,
                'lb': 0.453592, 'pound': 0.453592, 'pounds': 0.453592,
                'oz': 0.0283495, 'ounce': 0.0283495, 'ounces': 0.0283495,
                'ton': 1000, 'tons': 1000
            }
            
            # Storage conversions
            storage_units = {
                'b': 1, 'byte': 1, 'bytes': 1,
                'kb': 1024, 'kilobyte': 1024, 'kilobytes': 1024,
                'mb': 1024**2, 'megabyte': 1024**2, 'megabytes': 1024**2,
                'gb': 1024**3, 'gigabyte': 1024**3, 'gigabytes': 1024**3,
                'tb': 1024**4, 'terabyte': 1024**4, 'terabytes': 1024**4,
            }
            
            from_lower = from_unit.lower()
            to_lower = to_unit.lower()
            
            # Try each category
            if from_lower in length_units and to_lower in length_units:
                meters = value * length_units[from_lower]
                result_value = meters / length_units[to_lower]
            elif from_lower in weight_units and to_lower in weight_units:
                kg = value * weight_units[from_lower]
                result_value = kg / weight_units[to_lower]
            elif from_lower in storage_units and to_lower in storage_units:
                bytes_val = value * storage_units[from_lower]
                result_value = bytes_val / storage_units[to_lower]
            else:
                result["error"] = f"Can't convert {from_unit} to {to_unit}"
                return result
            
            result["status"] = "success"
            result["result"] = result_value
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def format_calculation(self, calc_result: Dict) -> str:
        """Format calculation result for display"""
        if calc_result["status"] != "success":
            return f"❌ Error: {calc_result.get('error', 'Unknown error')}"
        
        expr = calc_result["expression"]
        result = calc_result["formatted"]
        
        return f"""🧮 CALCULATION

   {expr}
   = {result}

✅ Answer: {result}"""
    
    def format_conversion(self, conv_result: Dict) -> str:
        """Format unit conversion for display"""
        if conv_result["status"] != "success":
            return f"❌ Can't convert: {conv_result.get('error', 'Unknown units')}"
        
        value = conv_result["value"]
        from_unit = conv_result["from"]
        to_unit = conv_result["to"]
        result = conv_result["result"]
        
        # Format nicely
        if isinstance(result, float):
            if result.is_integer():
                result_str = str(int(result))
            else:
                result_str = f"{result:.4f}".rstrip('0').rstrip('.')
        else:
            result_str = str(result)
        
        return f"""🔄 CONVERSION

   {value} {from_unit}
   = {result_str} {to_unit}

✅ Result: {result_str} {to_unit}"""

def main():
    """Test the calculator"""
    print("🧮 Testing CalculatorTool...\n")
    
    calc = CalculatorTool()
    
    test_expressions = [
        "5 plus 3",
        "10 times 2",
        "100 divided by 4",
        "sqrt(16)",
        "2 raised to 8",
        "pi times 2",
        "what is 50 minus 25"
    ]
    
    for expr in test_expressions:
        print(f"📝 {expr}")
        result = calc.calculate(expr)
        if result["status"] == "success":
            print(f"   ✅ = {result['formatted']}\n")
        else:
            print(f"   ❌ {result['error']}\n")
    
    # Test conversion
    print("\n🔄 Testing Unit Conversion:")
    conv = calc.convert_units(5, 'km', 'miles')
    print(calc.format_conversion(conv))
    
    conv = calc.convert_units(1024, 'mb', 'gb')
    print(calc.format_conversion(conv))

if __name__ == "__main__":
    main()