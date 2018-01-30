
class Currencies:
    
    def __init__(this):
        this.lookup = {};
        this.symbols = {};
        
    def getKey(this, key1, key2):    
        accessKey = "{0}:{1}";
        correctOrder = True;
        if key1 < key2:
            accessKey = accessKey.format(key1, key2);
        else:
            accessKey = accessKey.format(key2, key1);
            correctOrder = False;
            
        return KeyResult(accessKey, correctOrder);
    
    def keyExists(this, key):
        return this.symbols.get(key, False);
    
    def keysExist(this, fromKey, toKey):
        return this.keyExists(fromKey) and this.keyExists(toKey);
    
    def addConversion(this, fromKey, toKey, value):
        if not this.keysExist(fromKey, toKey):
            print("Invalid keys", fromKey, toKey);
            return;
        result = this.getKey(fromKey, toKey);
        if (result.correctOrder):
            this.lookup[result.key] = value;
        else:
            this.lookup[result.key] = 1/value;
            
    def getConversion(this, fromKey, toKey):
        if not this.keysExist(fromKey, toKey):
            print("WARNING: Invalid keys", fromKey, toKey);
            return 1;
        result = this.getKey(fromKey, toKey);
        if (result.correctOrder):
            return this.lookup[result.key];
        else:
            return 1 / this.lookup[result.key];
        
    def getFormattedConversion(this, fromKey, toKey, places=2):
        return round(this.getConversion(fromKey, toKey), places)
            
    def makeConversion(this, fromKey, toKey, value):
        if not this.keysExist(fromKey, toKey):
            print("WARNING: Invalid keys", fromKey, toKey);
            return value;
        return this.getConversion(fromKey, toKey) * value;
        
    def prettyConvert(this, fromKey, toKey, value):
        print("{0} => {1} at {2} : {3}{4} -> {5}{6}"
        .format(fromKey, toKey, this.getFormattedConversion(fromKey, toKey), this.getSymbol(fromKey),
                value, this.getSymbol(toKey), this.makeConversion(fromKey, toKey, value)));
        
    def addCurrency(this, key, symbol):
        this.symbols[key] = symbol;
    
    def getSymbol(this, key):
        return this.symbols.get(key, "");
            
    
            
    def print(this):
        print(this.lookup);
    
class KeyResult:
    def __init__(this, key, correctOrder):
        this.key = key;
        this.correctOrder = correctOrder;
        
currencies = Currencies();
currencies.addCurrency("GBP", "£");
currencies.addCurrency("USD", "$");
currencies.addCurrency("YEN", "S")
currencies.print();
currencies.addConversion("GBP", "USD", 1.6);
currencies.print();

currencies.prettyConvert("GBP", "USD", 1000);
currencies.prettyConvert("USD", "GBP", 1500);

currencies.addConversion("USD", "GBP", 2/3);
currencies.addConversion("YEN", "GBP", 1.3);
currencies.print();

currencies.prettyConvert("GBP", "USD", 1000);
currencies.prettyConvert("USD", "GBP", 1500);
currencies.prettyConvert("GBP", "YEN", 1500);
