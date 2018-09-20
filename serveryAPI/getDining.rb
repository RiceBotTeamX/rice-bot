$LOAD_PATH.unshift('.')
require_relative './rice-dining-master/lib/rice/dining' # problems
require 'csv'
require 'time'

#get argument for csv filename
ARGV.each do|a|
  puts "Argument: #{a}"
end

filename = ARGV[0]
manifest = Rice::Dining.manifest
timestamp = Time.now.utc.iso8601

CSV.open('./data/'+filename, 'w') do |csv|
  manifest.locations.each do |loc|
    loc.items.each do |item|
      csv << [loc.name, loc.open?, item.name, item.allergens.map(&:id).join(' ')]
    end
  end
end
