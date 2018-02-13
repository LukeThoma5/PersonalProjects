import pickle;

FILE_LOCATION = "currencies.bin";
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

    def getConversion(this, fromKey, toKey, attendedNodes=[], directIfAvailable=False):
        ## If specified we want direct route no matter what
        if directIfAvailable and this.getKey(fromKey, toKey).key in this.lookup:
            return ConversionResult(this.getConversionDirect(fromKey, toKey), [fromKey, toKey]);
        
        ## Otherwise find the best route, including direct routes
        lookupKeys = this.lookup.keys();
        conversions = [];
        for key in lookupKeys:
            # Get direct value if avalable
            if fromKey in key and toKey in key:
                conversions.append(ConversionResult(this.getConversionDirect(fromKey, toKey), [fromKey, toKey]));
            #If we find a key that contains a link to where we are
            elif fromKey in key:
                ## Find the other side of the link
                keys = key.split(':');
                indirectKey = keys[0];
                if indirectKey == fromKey:
                    indirectKey = keys[1];

                ## Check if we have already checked this node to prevent circular links
                if indirectKey in attendedNodes:
                    continue;
                #Create a copy of the attendedNodes values rather than creating a new reference to the existing array
                nodes = attendedNodes[:]; 
                nodes.append(fromKey); # Add on the node we are checking
                # Get the conversion for the single hop
                directConversion = this.getConversionDirect(fromKey, indirectKey); 
                # Get the conversion rate that was the result of all following hops
                tailConversion = this.getConversion(indirectKey, toKey, attendedNodes=nodes, directIfAvailable=directIfAvailable);
                # If we found a route back to the endpoint, add the link
                if (tailConversion.successful):
                    path = [fromKey]
                    path.extend(tailConversion.path)
                    conversion = ConversionResult(directConversion * tailConversion.rate, path);
                    conversions.append(conversion);
        #Sort the conversions in decending order of conversion rate, best first
        conversions.sort(key=lambda conversion: conversion.rate, reverse=True)
        #If we have a conversion return it
        if len(conversions) > 0:
            return conversions[0];
        #Otherwise we've failed to create a conversion
        print("WARNING: Invalid keys", fromKey, toKey);
        return ConversionResult(-1, [], successful=False);
            
    def getConversionDirect(this, fromKey, toKey):
        result = this.getKey(fromKey, toKey);
        if not result.key in this.lookup:
            print("WARNING: Invalid keys", fromKey, toKey);
            return -1;        
        if (result.correctOrder):
            return this.lookup[result.key];
        else:
            return 1 / this.lookup[result.key];
            
    def makeConversion(this, fromKey, toKey, value, directIfAvailable=False):
        if not this.keysExist(fromKey, toKey):
            print("WARNING: Invalid keys", fromKey, toKey);
            return ConversionResult(value, [], successful=False);
        return this.getConversion(
            fromKey,
            toKey,
            directIfAvailable=directIfAvailable).updateValue(value);
        
    def prettyConvert(this, fromKey, toKey, value, directIfAvailable=False):
        conversion = this.makeConversion(fromKey, toKey, value, directIfAvailable);
        if (conversion.successful):
            if (directIfAvailable):
                print("WARN: May not be best conversion! ", end="");
            print("{} at {} : {}{} -> {}{}"
            .format(
                conversion.getPath(),
                conversion.getRateFormatted(places=3),
                this.getSymbol(fromKey),
                value,
                this.getSymbol(toKey),
                conversion.getResultFormatted()
                ));
        else:
            print("Failed to convert {} => {}".format(fromKey, toKey));
        
    def addCurrency(this, key, symbol):
        this.symbols[key] = symbol;
    
    def getSymbol(this, key):
        return this.symbols.get(key, "");

    def print(this):
        print(this.lookup, this.symbols);

    def save(this):
        try:
            currencyfile = open(FILE_LOCATION, "wb");
            currencies = pickle.dump(this, currencyfile);
            currencyfile.close();
        except (e):
            print("Save failed!", e);

    def getGraphData(this):
        conversions = [];
        for fromKey in this.symbols:
            for toKey in this.symbols:
                if (fromKey != toKey):
                    conversions.append((this.getConversion(fromKey, toKey).rate,
                    this.getConversion(fromKey, toKey, directIfAvailable=True).rate));
        print(conversions);
        
class KeyResult:
    def __init__(this, key, correctOrder):
        this.key = key;
        this.correctOrder = correctOrder;

class ConversionResult:
    def __init__(this, rate, path = [], successful=True):
        this.rate = rate;
        this.path = path;
        this.value = 0;
        this.successful = successful;

    def updateValue(this, value):
        this.value = value * this.rate;
        return this; #Allow chaining of conversion results. Fluent syntax

    def getRateFormatted(this, places=2):
        return round(this.rate, places);

    def getResultFormatted(this, places=2):
        return round(this.value, places);

    def getPath(this):
        return ' => '.join(this.path);

    def __repr__(this):
        return this.__str__();

    def __str__(this):
        return "<Path: {}, Rate: {}, Success: {}>".format(
            this.getPath(),
            this.getRateFormatted(3),
            this.successful);

    def invert(this):
        this.rate = 1 / this.rate;
        this.path.reverse();

def seed_currencies(currencies):
    currencies.addCurrency("GBP", "£");
    currencies.addCurrency("USD", "$");
    currencies.addCurrency("EURO", "€");
    currencies.addCurrency("TEST", "T");
    currencies.addCurrency("YEN", "S");
    currencies.addConversion("GBP", "USD", 1.6);
    currencies.addConversion("USD", "EURO", 1.2);
    currencies.addConversion("EURO", "YEN", 1.4);
    currencies.addConversion("TEST", "YEN", 2);
    currencies.addConversion("GBP", "TEST", 2.4);
    currencies.addConversion("USD", "YEN", 0.5);

def main():
    currencies = Currencies();
    try:
        currencyfile = open(FILE_LOCATION, "rb");
        currencies = pickle.load(currencyfile);
        currencyfile.close();
    except:
        currencies = Currencies();
        seed_currencies(currencies);

    print("Initial state: ", end="");
    currencies.print();

    currencies.prettyConvert("USD", "YEN", 1500);
    currencies.prettyConvert("USD", "YEN", 1500, True);

    currencies.prettyConvert("NOTEXISTING", "USD", 1500);
    currencies.save();

    currencies.getGraphData();

main();
