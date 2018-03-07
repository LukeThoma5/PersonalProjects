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
    return ' => '.join(map(lambda x: x.name, this.path));

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
   