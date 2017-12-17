var gulp = require('gulp');
var postcss = require('gulp-postcss');
var tailwindcss = require('tailwindcss');

gulp.task('css', function () {
  return gulp.src('app/static/css/tailwind.css')
    // ...
    .pipe(postcss([
      // ...
      tailwindcss('tailwind.js'),
      require('autoprefixer'),
      // ...
    ]))
    // ...
    .pipe(gulp.dest('app/static/build/'));
});

gulp.task('default', [ 'css' ]);
gulp.watch('app/static/css/styles.css', ['css']);
