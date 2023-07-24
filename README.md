# md-translator script

This script is used for translating markdown files to different languages.

Some features:

- added correct shortcode translation. You a welcome to use any of custom shortcodes in your hugo theme, script will translate only the shortcode attributes. Also you can add the names of attributes you don't want to be translated in **ignore.txt** file using the following prompt:

````
shortcodes = avatar, slug
````

- separate params translation. Script will translatу frontmatter params separately for protecting your params keys
