const form = document.querySelector('.form');
const bibtexFile = 'anthology.json'; 
//const surveyFile = 'survey_form_data.json';

//let surveyObj = await getJson(surveyFile);
let surveyObj = {}
console.log('The survey text:', surveyObj);
//console.log("SO", surveyObj[bibkey]);
let bibtexObj  = await getJson(bibtexFile);   

function getJson(jsonFile) {
  let jsonObj = fetch(jsonFile)  
  .then(data => data.json()) 
  .catch(error => new Error(error));
  return jsonObj;
}



let bibkey = document.getElementById("bibKey").value;
console.log("bibkey:", bibkey); 
const surveyFile = bibkey + '.json'


const titleSpan  = document.querySelector("#title")
const authorSpan = document.querySelector("#author")
const yearSpan   = document.querySelector("#year")

if (bibtexObj.hasOwnProperty(bibkey)) {
  if ('TITLE' in bibtexObj[bibkey]) {
    titleSpan.textContent = bibtexObj[bibkey]['TITLE']
    authorSpan.textContent = bibtexObj[bibkey]['AUTHOR']
    yearSpan.textContent = bibtexObj[bibkey]['YEAR']
  } else {
    titleSpan.textContent = bibtexObj[bibkey]['title']
    authorSpan.textContent = bibtexObj[bibkey]['author']
    yearSpan.textContent = bibtexObj[bibkey]['year']
  }
  if (!surveyObj.hasOwnProperty(bibkey)) {
    surveyObj[bibkey] = {}
    if ('TITLE' in surveyObj[bibkey]) {
      surveyObj[bibkey] = {
        'title':  bibtexObj[bibkey]['TITLE'],
        'author': bibtexObj[bibkey]['AUTHOR'],
        'year': bibtexObj[bibkey]['YEAR']
      }
    } else {
      surveyObj[bibkey] = {
        'title':  bibtexObj[bibkey]['title'],
        'author': bibtexObj[bibkey]['author'],
        'year': bibtexObj[bibkey]['year']
      }
    }
  }
}
const writeToFile = (content, filename, contentType) => {
  const a = document.createElement('a');
  const file = new Blob([content], { type: contentType });
  
  a.href = URL.createObjectURL(file);
  a.download = filename;
  a.click();

  URL.revokeObjectURL(a.href);
}; 
 
/*
document.getElementById("surveyFile")
  .addEventListener("change", function () {
    var jr = new FileReader();
    var surveyFile = document.getElementById("surveyFile")
    surveyFile.innerHTML = "file:///home/ine/Desktop/html/survey_form_data.json"
    console.log("JR " + this.files[0])
    jr.readAsText(this.files[0]);
    jr.onload = function () {
      const surveyObj = JSON.parse(jr.result);
      console.log(surveyObj);

        console.log(surveyObj);
    };  
  });
*/    


/*
document.getElementById("surveyFile")
  .addEventListener("click", function () {
    var fr = new FileReader();
    console.log("FR " + this.files[0])
    fr.readAsText(this.files[0]);
    fr.onload = function () {
      surveyObj = JSON.parse(fr.result);
      console.log("survey obj", surveyObj); 
    }
  });
*/

/*
document.getElementById("bibtexFile")
  .addEventListener("click", function () {
    
    console.log("survey", surveyObj)
    var fr = new FileReader();
    console.log("FR " + this.files[0])
    fr.readAsText(this.files[0]);
    fr.onload = function () {
      const refObj = JSON.parse(fr.result);
      console.log("ref obj", refObj);
      bibkey = document.getElementById("bibKey").value;
      console.log("bibkey:", bibkey); 
      
      const titleSpan  = document.querySelector("#title")
      const authorSpan = document.querySelector("#author")
      const yearSpan   = document.querySelector("#year")

      titleSpan.textContent = refObj[bibkey]['TITLE']
      authorSpan.textContent = refObj[bibkey]['AUTHOR']
      yearSpan.textContent = refObj[bibkey]['YEAR']
    }
  });
*/

form.addEventListener('submit', (e) => {
  e.preventDefault();
  
  const formData = new FormData(e.currentTarget);
  const keys   = [...formData.keys()];
  const values = [...formData.values()];
  const missing = [];

  for (let i = 0; i < keys.length; i++) {
    console.log("next", keys[i], values[i]);
    if (values[i] == 'text') {
      const formElem = document.getElementById(keys[i]) 
      surveyObj[bibkey][keys[i]] = formElem.innerText;
      console.log("GOT TEXT FIELD: ", keys[i], formElem.innerText) 
    }
    else if (values[i] == '') {
      surveyObj[bibkey][keys[i]] = "--";
      missing.push(keys[i]);
    } else {
      console.log("adding to bibkey " + bibkey + " key " + keys[i] + " val " + values[i])
      console.log("BK", bibkey)
      console.log("SO", surveyObj)
      surveyObj[bibkey][keys[i]] = values[i]
    }  
  }
  const outputJSON = JSON.stringify(surveyObj, null, 3);

  /*
  if (missing.length > 0) {
    alert("Missing field: " + missing.join())
    console.log('Some please enter all values');
    // write json output to file
    writeToFile(outputJSON, surveyFile, "text")    
    return;
  } else {
    console.log("all ok...") 
    // write json output to file
    writeToFile(outputJSON, outfile, "text")
  }
  */

  // write json output to file
  writeToFile(outputJSON, surveyFile, "text")   

  const formObject = Object.fromEntries(formData);
  // do something
  document.write(formObject)
  //console.log("herexx", formObject);

  e.currentTarget.reset();
});




//body.append(title_elem)
