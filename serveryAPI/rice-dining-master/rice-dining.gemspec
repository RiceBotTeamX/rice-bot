require File.expand_path('../lib/rice/dining/version', __FILE__)

Gem::Specification.new do |s|
  s.name          =  'rice-dining'
  s.version       =  Rice::Dining::VERSION
  s.authors       =  ['Morgan Jones']
  s.email         =  'mjones@rice.edu'
  s.homepage      =  'https://numin.it'
  s.date          =  '2018-09-10'
  s.summary       =  'Gets Rice servery information'
  s.description   =  'Parses the HTML tag soup on the Rice dining homepage to get current servery information'
  s.license	      =  'MIT'
  s.files         =  `git ls-files`.split($\)
  s.require_paths = %w[lib]
  s.executables   << 'rice-dining'
  s.has_rdoc      = true
  s.required_ruby_version = '>= 2.0'
  s.add_dependency 'nokogiri', '~> 1.8'
  s.add_runtime_dependency 'colorize', '~> 0.8'
end
