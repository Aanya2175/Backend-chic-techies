import { 
  collection, 
  doc, 
  getDoc, 
  getDocs, 
  addDoc, 
  updateDoc, 
  query, 
  where,
  orderBy,
  Timestamp 
} from 'firebase/firestore';
import { db } from '@/config/firebase';

// Collection references
export const COLLECTIONS = {
  USERS: 'users',
  QUESTIONS: 'questions',
  LANGUAGES: 'languages', // subcollection under questions
  INPUTS: 'inputs',
  USER_ANSWERS: 'userAnswers',
  EVALUATION_RESULTS: 'evaluationResults',
  GPT_PROMPTS: 'gptPrompts',
  METRICS: 'metrics',
  AI_ANALYSIS: 'aiAnalysis',
  ACTIVITY_LOGS: 'activityLogs'
};

// Fetch all questions
export const getQuestions = async () => {
  try {
    const questionsRef = collection(db, COLLECTIONS.QUESTIONS);
    const snapshot = await getDocs(questionsRef);
    return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
  } catch (error) {
    console.error('Error fetching questions:', error);
    throw error;
  }
};

// Fetch question by ID with languages subcollection
export const getQuestionById = async (questionId: string) => {
  try {
    const questionRef = doc(db, COLLECTIONS.QUESTIONS, questionId);
    const questionDoc = await getDoc(questionRef);
    
    if (!questionDoc.exists()) {
      throw new Error('Question not found');
    }

    // Fetch languages subcollection
    const languagesRef = collection(questionRef, COLLECTIONS.LANGUAGES);
    const languagesSnapshot = await getDocs(languagesRef);
    const languages = languagesSnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));

    return {
      id: questionDoc.id,
      ...questionDoc.data(),
      languages
    };
  } catch (error) {
    console.error('Error fetching question:', error);
    throw error;
  }
};

// Submit user answer - writes to userAnswers collection
export const submitAnswer = async (userId: string, questionId: string, code: string, language: string) => {
  try {
    const answerData = {
      userId,
      questionId,
      code,
      language,
      submittedAt: Timestamp.now(),
      status: 'pending' // Backend will update this
    };

    const docRef = await addDoc(collection(db, COLLECTIONS.USER_ANSWERS), answerData);
    return docRef.id;
  } catch (error) {
    console.error('Error submitting answer:', error);
    throw error;
  }
};

// Fetch evaluation results for a user answer
export const getEvaluationResults = async (answerId: string) => {
  try {
    const resultsRef = collection(db, COLLECTIONS.EVALUATION_RESULTS);
    const q = query(resultsRef, where('answerId', '==', answerId));
    const snapshot = await getDocs(q);
    
    if (snapshot.empty) {
      return null;
    }
    
    const doc = snapshot.docs[0];
    return { id: doc.id, ...doc.data() };
  } catch (error) {
    console.error('Error fetching evaluation results:', error);
    throw error;
  }
};

// Fetch metrics for user
export const getUserMetrics = async (userId: string) => {
  try {
    const metricsRef = collection(db, COLLECTIONS.METRICS);
    const q = query(metricsRef, where('userId', '==', userId));
    const snapshot = await getDocs(q);
    return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
  } catch (error) {
    console.error('Error fetching metrics:', error);
    throw error;
  }
};

// Fetch AI analysis for user
export const getAIAnalysis = async (userId: string) => {
  try {
    const analysisRef = collection(db, COLLECTIONS.AI_ANALYSIS);
    const q = query(analysisRef, where('userId', '==', userId), orderBy('createdAt', 'desc'));
    const snapshot = await getDocs(q);
    return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
  } catch (error) {
    console.error('Error fetching AI analysis:', error);
    throw error;
  }
};

// Log activity
export const logActivity = async (userId: string, action: string, details: any) => {
  try {
    const activityData = {
      userId,
      action,
      details,
      timestamp: Timestamp.now()
    };
    
    await addDoc(collection(db, COLLECTIONS.ACTIVITY_LOGS), activityData);
  } catch (error) {
    console.error('Error logging activity:', error);
    throw error;
  }
};

// Fetch test inputs for a question
export const getTestInputs = async (questionId: string) => {
  try {
    const inputsRef = collection(db, COLLECTIONS.INPUTS);
    const q = query(inputsRef, where('questionId', '==', questionId));
    const snapshot = await getDocs(q);
    return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
  } catch (error) {
    console.error('Error fetching test inputs:', error);
    throw error;
  }
};
