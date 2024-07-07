import React, { useState, useEffect, useRef } from 'react'
import './App.css'
import axios from "axios";
import USAOlympicFlagImage from './assets/USAOlympicFlag.jpeg';

function App() {
  
  const loaded = useRef(false);
  const [gymnastArray, setGymnastArray] = useState({});
  const [appLoaded, setAppLoaded] = useState(false);

  useEffect(() => {
    // Simulate app loading process
    const simulateAppLoad = async () => {
      // Simulate a delay for app loading (e.g., other initialization processes)
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setAppLoaded(true);
    };

    simulateAppLoad();
  }, []);
    
  useEffect(() => {
    const fetchGymnastData = async () => {
      console.log("Fetching gymnast data...")
      setLoadingGymnastInputs(true);
      try {
        const response = await axios.get("http://localhost:8080/teamscenario/scores");
        setGymnastArray(response.data);
      } catch (error) {
        console.error("Error fetching gymnast data:", error);
      } finally {
        setLoadingGymnastInputs(false);
      }
    };
    
    if (appLoaded) {
      fetchGymnastData();
      loaded.current = true;
      console.log("Data fetched!");
    }
  }, [appLoaded]);
  
  // initialize gymnast array

  const [numTeamScenarios, setNumTeamScenarios] = useState(100);
  const indexToEventKey = {0:"FX", 1:"PH", 2:"SR", 3:"V", 4:"PB", 5:"HB"};

  // team scenarios handling
  const [teamScenariosArray, setTeamScenariosArray] = useState([]);
  const [loadingTeamScenarios, setLoadingTeamScenarios] = useState(false);
  const [loadingGymnastInputs, setLoadingGymnastInputs] = useState(false);

  // handle score change of input for each gymnast
  const handleScoreChange = (gymnastName, eventNumber, newValue) => {
    const eventScoreArray = [...gymnastArray[gymnastName]];
    eventScoreArray[eventNumber] = isNaN(newValue) || newValue === "" ? "" : newValue;
    setGymnastArray({
      ...gymnastArray,
      [gymnastName]: eventScoreArray
    });
  };

  // logs team scenarios array upon change
  useEffect(() => {
    console.log(teamScenariosArray);
  }, [teamScenariosArray]);

  // submit button
  const handleSubmit = async () => {
    console.time('handleSubmit');
    const copyGymnastArray = {...gymnastArray};
    // set any NaN scores to 0
    for (const gymnastName in copyGymnastArray) {
      copyGymnastArray[gymnastName] = copyGymnastArray[gymnastName].map(eventScore => (
        isNaN(eventScore) || eventScore == "" ? 0.0: eventScore
      ));
    }
    console.log("Posting data...");
    setLoadingTeamScenarios(true);
    // post data to main.py
    try {
      const response = await axios.post("http://localhost:8080/teamscenario/submit", {
        inputScores: copyGymnastArray,
        numTeamScenarios: numTeamScenarios
      });
      console.log("Setting team scenarios...");
      // add team scenarios to website
      setTeamScenariosArray(response.data);
    } catch (error) {
      console.error("Error submitting scores:", error);
    } finally {
      setLoadingTeamScenarios(false);
    }
    console.timeEnd('handleSubmit');
  };

  // change number of team scenarios
  const handleNumTeamScenarioChange = (newValue) => {
    setNumTeamScenarios(newValue);
  };

  return (
    <>
      <div className='container'>
        <header className='header'>
          <img src={USAOlympicFlagImage} alt="Example" className="header-image" />
          <h1>Men's Gymnastics Olympic Team Scenario Calculator</h1>
          <h3>Made by Jeremy Bischoff</h3>
        </header>
        <div className='instructions'>
          <h3>Instructions:</h3>
          <ul style={{ listStyleType: 'none' }}> 
            <li><b>1. Input scores for every competitor</b></li>
            <li><b>2. Select how many team scenarios you want to view</b></li>
            <li><b>3. Press submit to display the top team scenarios</b></li>
          </ul>
          <p><b>Feel free to play around and change any of the scores!</b></p>
          <span><b>Note: 4-day average scores for each competitor from both days of competition at the US Championships and Olympic Trials are initially shown.</b></span>
          <br></br>
          <span><b>Team scenarios are shown at the bottom of the page.</b></span>
        </div>
        
        <div className='submitContainer'>
          <button className='button' onClick={handleSubmit}>Submit</button>
          <input className='submitInput' type="number" value={numTeamScenarios} onChange={(e) => handleNumTeamScenarioChange(parseFloat(e.target.value))}></input>
        </div>
        
        {
          loadingGymnastInputs ? (
            <h3>Loading gymnast inputs...</h3>
          ) : (
            <div style={{display:'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap:'20px', justifyContent:'center', alignItems:'start'}}>
            {
              Object.keys(gymnastArray).map((gymnastName, index) => {
                return (
                  <div key={index}>
                    <h3>{gymnastName}: </h3>
                    {
                      gymnastArray[gymnastName].map((eventScore, index) => (
                        <React.Fragment key={index}>
                          <div className='inline-flex-container'>
                            <span className='eventName'><b>{indexToEventKey[index]}: </b></span>
                            <input className='textBox' type="number" value={eventScore} step="0.1" onChange={(e) => handleScoreChange(gymnastName, index, parseFloat(e.target.value))}></input>
                          </div>  
                        </React.Fragment>
                      ))
                    }
                  </div>
                );
              })
            }
        </div>
          )
        }

        {
          loadingTeamScenarios ? (
            <h3 >Calculating team scenarios...</h3>
          ) : (
            <div style={{display:'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap:'30px'}}>
            {
              teamScenariosArray.map((data, rank) => (
                <div className='teamScenarioInfo' key={rank}>
                    <h3>{rank+1}.</h3>
                    <span>Team Score: {data["teamScore"]} </span>
                    <br></br>
                    {
                      data["fiveManTeam"].map((name, key) => (
                        <span key={key}>{key == 0 && "Team: "}{name}{key < data["fiveManTeam"].length - 1 && ", "}</span>
                      ))
                    }
                </div>
                
              ))
            }
        </div>
          )
        }
      </div>
      
      
      
    </>
  )
}

export default App
