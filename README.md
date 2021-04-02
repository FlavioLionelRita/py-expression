

# Parser

Parser is the main class of the library that contains the methods to parse, evaluate and simplify mathematical expressions. In order to use the library you need to create an instance of this class:

```python
from py_expression.core import Parser

parser = Parser()

```
## Parse

```python
from py_expression.core import Parser

parser = Parser()
operand =parser.parse('a+4')
```

## Eval

```python
from py_expression.core import Parser

parser = Parser()
operand =parser.parse('a+4')
result = operand.eval({"a":2})
```

```python
from py_expression.core import Parser

parser = Parser()
result =parser.parse('a+4').eval({"a":2})
```

## Work with expressions

reuse the parsed expression:
```python
from py_expression.core import Parser

parser = Parser()
op = parser.parse('sin(x)') 
xs=[]
ys=[] 
for x in range(-100,100):
    y=op.eval({"x":x})
    xs.append(x)
    ys.append(y)  
```

create a new expression based on two or more parsed expressions:
```python
from py_expression.core import Parser

parser = Parser()
parser = Parser()
op1 = parser.parse('a+1')
op2 = parser.parse('b')
op3 = (op1+op2)*(op1-op2) >= (op1*2)

resutl1= op3.eval({"a":1,"b":2})
resutl2= op3.eval({"a":5,"b":9})
```





# Operators

## Arithmetic Operators
```python
context = {"a":9,"b":4,"c":{"a":4,"b":5},"d":None}
```

|operator | example      | result
|:------- | :----------  | :----------
|    +    |  a + 5       | 14
|    -    |  a - 1       | 8
|    *    |  a * b       | 36
|    **   |  a ** c.a    | 6561   
|    /    |  a / 4       | 2.25
|    //   |  a // c.b    | 1
|    %    |  a % 2       | 1

### Combinations

| example            | result
|:-------------      | :----------
|    3+2-1           |   4
|    1+4*2           |   9
|    3*4-1           |   11
|    1-2-5           |   -6  
|    (1+4)*2         |   10
|    2*(3+2)*(2+2)   |   40
|    1+(2**3)*4      |   33
|    -1+2**(3*4)     |   4095

## Assignment Operators
```python
context = {"a":9,"b":4,"c":{"a":4,"b":5},"d":None}
```

|operator | example      | result
|:------- | :----------  | :----------
|    =    |  a = 5       | 5
|    +=   |  a += 1      | 10
|    -=   |  a -= b      | 5
|    *=   |  a *= c.a    | 36   
|    /=   |  a /= 4      | 2.25
|    %=   |  a %= c.b    | 4
|    **=  |  a **= 2     | 81


## Comparison Operators    
```python
context = {"a":9,"b":4,"c":{"a":4,"b":5},"d":None}
```

|operator | example      | result
|:------- | :------------| :----------
|   ==    |a == 5        |False
|   !=    |a != 5        |True
|   >     |a > b         |True
|    <    |a < c.a       |False   
|    >=   |a >= 4        |True
|    <=   |a <= c.b      |False

##  Logical Operators

```python
context = {"a":9,"b":4,"c":{"a":4,"b":5},"d":None}
```
|operator | example              | result
|:------- | :----------          | :----------
|    &&   |  b == c.a && a>b     | True
|   &#124;&#124;   |  b != c.a &#124;&#124; a>b     | True
|    !    |  !(b != c.a &#124;&#124; a>b)  | False


## Bitwise Operators

|operator | example              | result
|:------- | :----------          | :----------
| &       |  5 & 1               |  	 1
| &#124;  |  5 &#124; 1          |  5
| ^       |  5 ^ 1               |  4
| <<      |  5 << 1              |  10
| >>      |  5 >> 1              |  2


# Objects
```python
context = {"a":1,"b":{"c":1}}
```

| example               | result
|:-------------         | :----------
| 'x={a:1}'             | {'a': 1, 'b': {'c': 1}, 'x': {'a': 1}}  
| 'a={a:1}'             | {'a': {'a': 1}, 'b': {'c': 1}}
| 'b.c=a+1'             | {'a': 1, 'b': {'c': 2}}

# Arrays
```python
context = {"a":[1,2,3],"b":2}
```

| example               | result
|:-------------         | :----------
| 'a[0]'                | 1
| 'a[b]'                | 3
| 'a[b-1]'              | 2

# Enums

```python
exp.addEnum('ColorConversion',{"BGR2GRAY":6
                             ,"BGR2HSV":40
                             ,"BGR2RGB":4
                             ,"GRAY2BGR":8
                             ,"HSV2BGR":54
                             ,"HSV2RGB":55
                             ,"RGB2GRAY":7
                             ,"RGB2HSV":41})
```

| example                    | result
|:-------------              | :----------
| 'ColorConversion.GRAY2BGR' | 8 


## Math Functions

| function               | description
|:-------------          | :----------
| ceil(x)| Returns the smallest integer greater than or equal to x.
| copysign(x, y) | Returns x with the sign of y
| fabs(x)| Returns the absolute value of x
| factorial(x) | Returns the factorial of x
| floor(x) | Returns the largest integer less than or equal to x
| fmod(x, y) | Returns the remainder when x is divided by y
| frexp(x) | Returns the mantissa and exponent of x as the pair (m, e)
| fsum(iterable) | Returns an accurate floating point sum of values in the iterable
| isfinite(x) | Returns True if x is neither an infinity nor a NaN (Not a Number)
| isinf(x) | Returns True if x is a positive or negative infinity
| isnan(x) | Returns True if x is a NaN
| ldexp(x, i) | Returns x * (2**i)
| modf(x) | Returns the fractional and integer parts of x
| trunc(x) | Returns the truncated integer value of x
| exp(x) | Returns e**x
| expm1(x) | Returns e**x - 1
| log(x[, b]) | Returns the logarithm of x to the base b (defaults to e)
| log1p(x) | Returns the natural logarithm of 1+x
| og2(x) | Returns the base-2 logarithm of x
| log10(x) | Returns the base-10 logarithm of x
| pow(x, y) | Returns x raised to the power y
| sqrt(x) | Returns the square root of x
| acos(x) | Returns the arc cosine of x
| asin(x) | Returns the arc sine of x
| atan(x) | Returns the arc tangent of x
| atan2(y, x) | Returns atan(y / x)
| cos(x) | Returns the cosine of x
| hypot(x, y) | Returns the Euclidean norm, sqrt(x*x + y*y)
| sin(x) | Returns the sine of x
| tan(x) | Returns the tangent of x
| degrees(x) | Converts angle x from radians to degrees
| radians(x) | Converts angle x from degrees to radians
| acosh(x) | Returns the inverse hyperbolic cosine of x
| asinh(x) | Returns the inverse hyperbolic sine of x
| atanh(x) | Returns the inverse hyperbolic tangent of x
| cosh(x) | Returns the hyperbolic cosine of x
| sinh(x) | Returns the hyperbolic cosine of x
| tanh(x) | Returns the hyperbolic tangent of x
| erf(x) | Returns the error function at x
| erfc(x) | Returns the complementary error function at x
| gamma(x) | Returns the Gamma function at x
| lgamma(x) | Returns the natural logarithm of the absolute value of the Gamma function at x
| pi() | Mathematical constant, the ratio of circumference of a circle to it's diameter (3.14159...)
| e() | mathematical constant e (2.71828...)

# Strings

| example               | result
|:-------------         | :----------
| '"a"'                 | a 
| '"a"<"b"'             | True 
| 'nvl(c,b)'            | c  
| 'a.capitalize()'      | Aaa    
| '"aaa".capitalize()'  | Aaa   
| 'a.count("a")'        | 3
| 'a.count("b")'        | 0 
| 'a.upper()'           | AAA  
| '"a"+a+b'             | aaaab   




## String Functions
| function               | description
|:-------------          | :----------
|capitalize( 	) | Return a copy of the string with only its first character capitalized. 
|center( 	width[, fillchar]) | Return centered in a string of length width. Padding is done using the specified fillchar
|count( 	sub[, start[, end]]) | Return the number of occurrences of substring sub in string 
|decode( 	[encoding[, errors]]) |Decodes the string using the codec registered for encoding. encoding defaults to the default string encoding. 
|encode( 	[encoding[,errors]]) |Return an encoded version of the string. Default encoding is the current default string encoding.
| endswith( 	suffix[, start[, end]])|Return True if the string ends with the specified suffix, otherwise return False.
|expandtabs( 	[tabsize]) |Return a copy of the string where all tab characters are expanded using spaces. If tabsize is not given, a tab size of 8 characters is assumed. 
| find( 	sub[, start[, end]])|Return the lowest index in the string where substring sub is found, such that sub is contained in the range [start, end]. 
|index( 	sub[, start[, end]]) |Like find(), but raise ValueError when the substring is not found. 
|isalnum( 	) |Return true if all characters in the string are alphanumeric and there is at least one character, false otherwise. 
|isalpha( 	) |Return true if all characters in the string are alphabetic and there is at least one character, false otherwise. 
|isdigit( 	)|Return true if all characters in the string are digits and there is at least one character, false otherwise. 
| islower( 	)|Return true if all cased characters in the string are lowercase and there is at least one cased character, false otherwise. 
|isspace( 	)| Return true if there are only whitespace characters in the string and there is at least one character, false otherwise. 
|istitle( 	) |Return true if the string is a titlecased string and there is at least one character, for example uppercase characters may only follow uncased characters and lowercase characters only cased ones.
|isupper( 	) |Return true if all cased characters in the string are uppercase and there is at least one cased character, false otherwise. 
|join( 	seq) |Return a string which is the concatenation of the strings in the sequence seq. The separator between elements is the string providing this method. 
|ljust( 	width[, fillchar]) |Return the string left justified in a string of length width. Padding is done using the specified fillchar (default is a space).
|lower( 	) |Return a copy of the string converted to lowercase. 
|lstrip( 	[chars])|Return a copy of the string with leading characters removed. 
|partition( 	sep) |Split the string at the first occurrence of sep, and return a 3-tuple containing the part before the separator, the separator itself, and the part after the separator. 
|rfind( 	sub [,start [,end]]) |Return the highest index in the string where substring sub is found, such that sub is contained within s[start,end].
|rindex( 	sub[, start[, end]])|Like rfind() but raises ValueError when the substring sub is not found. 
|rjust( 	width[, fillchar]) | Return the string right justified in a string of length width. Padding is done using the specified fillchar (default is a space).
|rpartition( 	sep) |Split the string at the last occurrence of sep, and return a 3-tuple containing the part before the separator, the separator itself, and the part after the separator. If the separator is not found, return a 3-tuple containing two 
| rsplit( 	[sep [,maxsplit]])|Return a list of the words in the string, using sep as the delimiter string. If maxsplit is given, at most maxsplit splits are done, the rightmost ones
| rstrip( 	[chars])| Return a copy of the string with trailing characters removed
|split( 	[sep [,maxsplit]]) | Return a list of the words in the string, using sep as the delimiter string. If maxsplit is given, at most maxsplit splits are done. (thus, the list will have at most maxsplit+1 elements). 
|splitlines( 	[keepends]) |Return a list of the lines in the string, breaking at line boundaries. Line breaks are not included in the resulting list unless keepends is given and true. 
| startswith( 	prefix[, start[, end]])| Return True if string starts with the prefix, otherwise return False. prefix can also be a tuple of prefixes to look for. With optional start, test string beginning at that position.
|strip( 	[chars]) |Return a copy of the string with the leading and trailing characters removed. The chars argument is a string specifying the set of characters to be removed. 
|swapcase( 	) | Return a copy of the string with uppercase characters converted to lowercase and vice versa. 
|title( 	) | Return a titlecased version of the string: words start with uppercase characters, all remaining cased characters are lowercase. 
|upper( 	) | Return a copy of the string converted to uppercase. 
|zfill( 	width) |Return the numeric string left filled with zeros in a string of length width. The original string is returned if width is less than len(s)

